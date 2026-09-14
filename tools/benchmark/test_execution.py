"""Public offline harness tests. Synthetic samples here are NOT benchmark tasks."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import suite
import study


def toy():
    data={'kind':'io','tests':[{'id':'feature','kind':'feature','input':2,'expected':4},
                             {'id':'regression','kind':'regression','input':0,'expected':0}],
          'reference_files':{'app.py':'import json,sys\nprint(json.load(sys.stdin)*2)\n'},
          'alternative_files':{'app.py':'import json,sys\nx=json.load(sys.stdin);print(x+x)\n'},
          'mutants':[{'name':'wrong','files':{'app.py':'print(0)\n'}}]}
    task={'id':'FIX-99','version':1,'language':'python','source_family':'toy','split':'development',
          'files':{'app.py':'print(0)\n'},'user_overlay':{'notes.txt':'keep\n'},'task':'Double the integer.',
          'submission_mode':'workspace','author_seconds':1200,'evaluator_sha256':suite.digest(data),
          'checks_sha256':suite.digest([{'id':'feature','kind':'feature'},{'id':'regression','kind':'regression'}])}
    task['package_sha256']=suite.digest(task)
    catalog={'schema_version':1,'inference_authorized':False,'smoke_task_ids':['FIX-99'],'tasks':[task]}
    return task,data,catalog


def protocol():
    return {'comparison_kind':'globals_and_delegation','conditions':[
        {'id':'A','globals':'none','helpers_enabled':True,'helper_route':'shared'},
        {'id':'B','globals':'non_delegation','helpers_enabled':False,'helper_route':None},
        {'id':'C','globals':'full','helpers_enabled':True,'helper_route':'shared'}],
        'submission':{'commit_required':False},'primary_contrasts':[['C','A'],['C','B']]}


def usage():
    return {'usage_scope':'own_session_only','complete':True,'sessions':[
        {'session_id':'root','parent_id':None,'model':'root-model','effort':'high',
         'tokens':{'input_tokens':1000000,'cached_input_tokens':500000,'output_tokens':100000,'reasoning_output_tokens':50000}},
        {'session_id':'child','parent_id':'root','model':'child-model','effort':'max',
         'tokens':{'input_tokens':100000,'cached_input_tokens':0,'output_tokens':10000}}]}


def rates(): return {'models':{'root-model':[10,1,50],'child-model':[1,0.1,5]}}


def good_review(sha):
    return {'artifact_sha256':sha,'reviewer_kind':'human','reviewer_id':'fixture-reviewer',
            'evidence':'Synthetic test evidence only.','blocker':False,
            'scores':dict.fromkeys(study.DIMENSIONS,2)}


class CatalogAndGradingTests(unittest.TestCase):
    def test_real_catalog_has_twelve_development_cases_in_three_languages(self):
        c=suite.load_catalog();self.assertEqual(len(c['tasks']),12)
        self.assertEqual({t['language'] for t in c['tasks']},{'python','typescript','go'})
        self.assertTrue(all(t['split']=='development' for t in c['tasks']))
        self.assertEqual(len(c['smoke_task_ids']),4)

    def test_tampered_source_fails_hash(self):
        t,_,_=toy();t['files']['app.py']='bad'
        with self.assertRaises(suite.Invalid):suite.validate_task(t)

    def test_unsafe_paths_are_rejected(self):
        for name in ['../x','/x','a/../x','.git/config','C:/x','a\\x','a//b']:
            with self.subTest(name=name),self.assertRaises(suite.Invalid):suite.relative(name)

    def test_duplicate_json_keys_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'x.json';p.write_text('{"a":1,"a":2}')
            with self.assertRaises(suite.Invalid):suite.read_json(p)

    def test_nonfinite_json_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'x.json';p.write_text('{"a":NaN}')
            with self.assertRaises(suite.Invalid):suite.read_json(p)

    def test_export_keeps_overlay_untracked(self):
        t,_,_=toy()
        with tempfile.TemporaryDirectory() as td:
            target=Path(td)/'task';suite.materialize(t,target)
            self.assertEqual((target/'notes.txt').read_text(),'keep\n')
            status=suite.command(['git','status','--porcelain'],target)
            self.assertIn('?? notes.txt',status.stdout)
            self.assertIn('Double the integer',(target/'TASK.md').read_text())

    def test_export_never_reuses_workspace(self):
        t,_,_=toy()
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(FileExistsError):suite.materialize(t,Path(td))

    def test_export_never_writes_inside_repository(self):
        t,_,_=toy()
        with self.assertRaises(suite.Invalid):suite.materialize(t,suite.ROOT/'must-not-create')

    def test_snapshot_rejects_symlink(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'target').write_text('x');(root/'link').symlink_to(root/'target')
            with self.assertRaises(suite.Invalid):suite.snapshot(root)

    def test_evaluator_hash_is_enforced(self):
        t,e,_=toy();e['tests'][0]['expected']=42
        with self.assertRaises(suite.Invalid):suite.evaluator(t,{'tasks':{t['id']:e}})

    def test_reference_alternative_and_noop_controls(self):
        t,e,c=toy();r=suite.controls(c,{'tasks':{t['id']:e}})
        self.assertEqual(r['control_count'],4);self.assertTrue(all(x['control_passed'] for x in r['controls']))
        self.assertFalse(r['runtime_isolation_validated']);self.assertEqual(r['model_calls'],0)

    def test_lost_user_overlay_fails_integrity(self):
        t,e,_=toy();r=suite.grade_files(t,e,{**t['files'],**e['reference_files']})
        self.assertTrue(r['functional_pass']);self.assertFalse(r['integrity_pass'])

    def test_python_boolean_is_not_integer_expected_output(self):
        t,e,_=toy();e['tests'][0]['expected']=1
        r=suite.grade_files(t,e,{'app.py':'print("true")','notes.txt':'keep\n'})
        self.assertFalse(r['functional_pass'])

    def test_process_timeout_is_recorded(self):
        with tempfile.TemporaryDirectory() as td:
            r=suite.command([sys.executable,'-S','-c','import time;time.sleep(5)'],Path(td),timeout=0.02)
            self.assertEqual(r.returncode,124)

    def test_sandbox_does_not_receive_answers_or_reference(self):
        t,e,_=toy();observed={}
        def fake_command(argv,cwd,**kwargs):
            if argv[1]=='run':
                request=suite.read_json(cwd/'request.json');observed.update(request)
                return subprocess.CompletedProcess(argv,0,json.dumps({'outputs':[]}), '')
            return subprocess.CompletedProcess(argv,0,'','')
        with patch.object(suite.shutil,'which',return_value='/usr/bin/docker'),patch.object(suite,'command',side_effect=fake_command):
            suite.sandbox_observe(t,t['files'],[2,0],'io','grader@sha256:'+'a'*64)
        self.assertEqual(set(observed),{'task','files','inputs','mode'})
        self.assertNotIn('evaluator_sha256',observed['task'])
        self.assertNotIn('reference_files',observed)

    def test_sandbox_requires_digest_pin(self):
        t,_,_=toy()
        with self.assertRaises(suite.Invalid):suite.sandbox_observe(t,t['files'],[],'io','grader:latest')

    def test_untrusted_code_never_falls_back_to_local(self):
        t,_,_=toy()
        with patch.object(suite.shutil,'which',return_value=None),self.assertRaises(suite.Invalid):
            suite.sandbox_observe(t,t['files'],[],'io','grader@sha256:'+'a'*64)


class AccountingTests(unittest.TestCase):
    def test_root_helper_and_cache_accounting(self):
        r=study.price_usage(usage(),rates())
        self.assertAlmostEqual(r['root_credits'],10.5);self.assertAlmostEqual(r['helper_credits'],0.15)
        self.assertAlmostEqual(r['known_credits'],10.65)

    def test_reasoning_not_double_charged(self):
        u=usage();a=study.price_usage(u,rates());u['sessions'][0]['tokens']['reasoning_output_tokens']=0
        self.assertEqual(a['known_credits'],study.price_usage(u,rates())['known_credits'])

    def test_duplicate_session_rejected(self):
        u=usage();u['sessions'].append(copy.deepcopy(u['sessions'][0]))
        with self.assertRaises(suite.Invalid):study.price_usage(u,rates())

    def test_missing_parent_and_cycle_rejected(self):
        for parent in ['absent','child']:
            u=usage();u['sessions'][1]['parent_id']=parent
            with self.subTest(parent=parent),self.assertRaises(suite.Invalid):study.price_usage(u,rates())

    def test_multiple_roots_rejected(self):
        u=usage();u['sessions'][1]['parent_id']=None
        with self.assertRaises(suite.Invalid):study.price_usage(u,rates())

    def test_inherited_history_cannot_be_costed_as_own_usage(self):
        u=usage();u['usage_scope']='includes_parent_history'
        with self.assertRaises(suite.Invalid):study.price_usage(u,rates())

    def test_cached_input_not_additional_input(self):
        u=usage();u['sessions'][0]['tokens']['cached_input_tokens']=2000000
        with self.assertRaises(suite.Invalid):study.price_usage(u,rates())

    def test_unknown_model_is_not_free(self):
        u=usage();u['sessions'][1]['model']='unknown'
        with self.assertRaises(suite.Invalid):study.price_usage(u,rates())

    def test_missing_usage_is_marked_incomplete(self):
        u=usage();u['sessions'][1]['tokens']=None
        r=study.price_usage(u,rates());self.assertFalse(r['complete']);self.assertEqual(r['known_credits'],10.5)

    def test_no_sessions_is_not_complete_zero_cost(self):
        with self.assertRaises(suite.Invalid):study.price_usage({'usage_scope':'own_session_only','complete':True,'sessions':[]},rates())
        r=study.price_usage({'usage_scope':'own_session_only','complete':False,'sessions':[]},rates())
        self.assertFalse(r['complete'])

    def test_negative_or_boolean_tokens_rejected(self):
        for value in [-1,True]:
            u=usage();u['sessions'][0]['tokens']['output_tokens']=value
            with self.subTest(value=value),self.assertRaises(suite.Invalid):study.price_usage(u,rates())

    def test_nonfinite_rates_rejected(self):
        r=rates();r['models']['root-model'][0]='NaN'
        with self.assertRaises(suite.Invalid):study.price_usage(usage(),r)


class StudyTests(unittest.TestCase):
    def setUp(self):
        self.task,self.evaluator,self.catalog=toy()
        self.doc=study.schedule(self.catalog,['A','B','C'],['FIX-99'],2,11,protocol())
        self.grade={'task_id':self.task['id'],'task_sha256':self.task['package_sha256'],
                    'evaluator_sha256':self.task['evaluator_sha256'],'artifact_sha256':'a'*64,
                    'integrity_pass':True,'execution':'docker_untrusted','tests':[
                       {'id':'feature','kind':'feature','passed':True},
                       {'id':'regression','kind':'regression','passed':True}]}

    def row(self,slot=0,passed=True):
        grade=copy.deepcopy(self.grade);grade['tests'][0]['passed']=passed
        return study.make_record(self.doc,self.doc['runs'][slot]['run_id'],grade,usage(),rates(),'completed','simulation')

    def test_schedule_deterministic_complete_and_blocked(self):
        b=study.schedule(self.catalog,['A','B','C'],['FIX-99'],2,11,protocol())
        self.assertEqual(self.doc,b);self.assertEqual(len(b['runs']),6)
        self.assertFalse(b['inference_authorized']);study.verify_schedule(b)

    def test_bad_causal_comparison_rejected(self):
        p=protocol();p['conditions'][0]['helpers_enabled']=False
        with self.assertRaises(suite.Invalid):study.schedule(self.catalog,['A','B','C'],['FIX-99'],1,2,p)

    def test_duplicate_tasks_and_zero_repeats_rejected(self):
        for ids,repeats in [(['FIX-99','FIX-99'],1),(['FIX-99'],0)]:
            with self.assertRaises(suite.Invalid):study.schedule(self.catalog,['A','B','C'],ids,repeats,1,protocol())

    def test_tampered_schedule_rejected(self):
        self.doc['runs'].pop()
        with self.assertRaises(suite.Invalid):study.verify_schedule(self.doc)

    def test_empty_results_are_partial_not_success(self):
        r=study.summarize(self.doc,[])
        self.assertEqual(r['status'],'partial');self.assertEqual(len(r['missing_run_ids']),6)
        self.assertEqual(r['promotion'],'not_evaluated')

    def test_missing_review_does_not_mean_accepted(self):
        row=self.row();self.assertIsNone(study.acceptable(row))
        r=study.summarize(self.doc,[row])['conditions'][row['condition']]
        self.assertEqual(r['pending_quality_reviews'],1);self.assertIsNone(r['task_weighted_cost_per_acceptable'])

    def test_failed_attempt_still_costs_money(self):
        rows=[self.row(i,passed=i<3) for i in range(6)]
        for row in rows:
            if row['functional_pass']:row['review']=good_review(row['artifact_sha256'])
        r=study.summarize(self.doc,rows)
        for arm in r['conditions'].values():
            self.assertAlmostEqual(arm['known_workflow_credits'],21.3)
            self.assertAlmostEqual(arm['task_weighted_cost_per_acceptable'],21.3)
        self.assertFalse(r['contrasts'])  # Simulations cannot support efficacy claims.

    def test_no_success_cost_is_undefined_not_zero(self):
        row=self.row(passed=False);r=study.summarize(self.doc,[row])
        self.assertIsNone(r['conditions'][row['condition']]['task_weighted_cost_per_acceptable'])

    def test_invalid_without_grade_retains_spending(self):
        row=study.make_record(self.doc,self.doc['runs'][0]['run_id'],None,usage(),rates(),
                              'infrastructure_error','simulation','grader unavailable')
        arm=study.summarize(self.doc,[row])['conditions'][row['condition']]
        self.assertEqual(arm['valid'],0);self.assertAlmostEqual(arm['known_infrastructure_credits'],10.65)

    def test_omitting_checks_is_rejected(self):
        grade=copy.deepcopy(self.grade);grade['tests'].pop()
        with self.assertRaises(suite.Invalid):study.make_record(self.doc,self.doc['runs'][0]['run_id'],grade,usage(),rates(),'completed','simulation')

    def test_imported_local_control_is_rejected(self):
        grade=copy.deepcopy(self.grade);grade['execution']='trusted_local_control'
        with self.assertRaises(suite.Invalid):study.make_record(self.doc,self.doc['runs'][0]['run_id'],grade,usage(),rates(),'completed','imported')

    def test_duplicate_records_are_rejected(self):
        r=self.row()
        with self.assertRaises(suite.Invalid):study.summarize(self.doc,[r,r])

    def test_mixed_simulated_and_imported_records_rejected(self):
        a=self.row(0);b=self.row(1);b['execution_kind']='imported'
        with self.assertRaises(suite.Invalid):study.summarize(self.doc,[a,b])

    def test_mixed_rate_cards_rejected(self):
        a=self.row(0);b=self.row(1);b['cost']['rate_card_sha256']='other'
        with self.assertRaises(suite.Invalid):study.summarize(self.doc,[a,b])

    def test_human_review_is_hash_bound(self):
        r=good_review('a'*64)
        with self.assertRaises(suite.Invalid):study.validate_review(r,'b'*64)

    def test_missing_human_evidence_is_rejected(self):
        r=good_review('a'*64);r['reviewer_kind']='model'
        with self.assertRaises(suite.Invalid):study.validate_review(r,'a'*64)

    def test_review_blocker_or_bad_dimension_rejects_acceptance(self):
        row=self.row();row['review']=good_review(row['artifact_sha256']);row['review']['scores']['appropriate_complexity']=1
        self.assertFalse(study.acceptable(row));row['review']['scores']['appropriate_complexity']=2
        row['review']['blocker']=True;self.assertFalse(study.acceptable(row))

    def test_small_group_uncertainty_is_withheld(self):
        rows=[self.row(i) for i in range(6)]
        for r in rows:r['review']=good_review(r['artifact_sha256'])
        comparison=study.paired_contrast(rows,'C','A',1,2)
        self.assertEqual(comparison['paired_tasks'],1);self.assertIsNone(comparison['intervals'])

    def test_prepare_runs_no_model_or_credentials(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'study';doc=study.prepare(self.catalog,protocol(),['FIX-99'],1,1,out)
            self.assertEqual(len(list((out/'workspaces').iterdir())),3)
            self.assertFalse(doc['inference_authorized'])
            self.assertEqual(suite.read_json(out/'readiness.json')['model_calls'],0)

    def test_helper_in_disabled_import_is_invalid_not_free(self):
        slot=next(r for r in self.doc['runs'] if r['condition']=='B')
        row=study.make_record(self.doc,slot['run_id'],self.grade,usage(),rates(),'completed','imported')
        self.assertIn('Helper observed',row['invalid_reason'])
        self.assertAlmostEqual(row['cost']['known_credits'],10.65)

    def test_cluster_bootstrap_preserves_paired_cost_ratio(self):
        rows=[]
        for i in range(6):
            for condition,cost in [('A',20),('C',10)]:
                r=self.row();r.update(task_id=f't{i}',repeat=1,condition=condition,source_family=f'g{i}')
                r['cost']['known_credits']=cost;r['review']=good_review(r['artifact_sha256']);rows.append(r)
        result=study.paired_contrast(rows,'C','A',7,2,resamples=100)
        self.assertEqual(result['intervals']['cost_per_acceptable_ratio'],[0.5,0.5])
        self.assertEqual(result['intervals']['acceptance_difference'],[0.0,0.0])

    def test_zero_success_bootstrap_draws_not_silently_dropped(self):
        rows=[]
        for i in range(6):
            for condition in ['A','C']:
                r=self.row(passed=condition=='A');r.update(task_id=f't{i}',repeat=1,condition=condition,source_family=f'g{i}')
                r['review']=good_review(r['artifact_sha256']);rows.append(r)
        result=study.paired_contrast(rows,'C','A',7,2,resamples=100)
        self.assertIsNone(result['intervals']['cost_per_acceptable_ratio'])
        self.assertIn('no draws discarded',result['ratio_note'])

    def test_review_packets_remove_labels_and_reject_stale_work(self):
        with tempfile.TemporaryDirectory() as td:
            parent=Path(td);root=parent/'study'
            doc=study.prepare(self.catalog,protocol(),['FIX-99'],1,4,root)
            slot=doc['runs'][0];workspace=root/'workspaces'/slot['run_id']
            suite.put_files(workspace,self.evaluator['reference_files'])
            grade=suite.grade_files(self.task,self.evaluator,suite.snapshot(workspace))
            row=study.make_record(doc,slot['run_id'],grade,usage(),rates(),'completed','simulation')
            suite.write_new(root/'records'/f"{slot['run_id']}.json",row)
            out=parent/'packets';mapping=parent/'private-map.json'
            result=study.review_packets(root,out,mapping);self.assertEqual(result['packets'],1)
            review_path=next(out.glob('*/review.json'));review=suite.read_json(review_path)
            self.assertNotIn('condition',review);self.assertIsNone(review['reviewer_id'])
            (workspace/'app.py').write_text('print(42)')
            with self.assertRaises(suite.Invalid):study.review_packets(root,parent/'stale',parent/'stale-map.json')

    def test_commit_protocol_is_not_silently_graded_as_workspace(self):
        p=protocol();p['submission']['commit_required']=True
        with self.assertRaises(suite.Invalid):study.schedule(self.catalog,['A','B','C'],['FIX-99'],1,1,p)

    def test_markdown_report_labels_missing_evidence(self):
        text=study.markdown_report(study.summarize(self.doc,[]))
        self.assertIn('Missing review is not acceptance',text)
        self.assertIn('Not evaluated',text)


if __name__=='__main__':unittest.main()
