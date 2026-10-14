"""#46：原版災難城市正常運行取得核能施工資金，不改資料或亂數。"""
import json
import os
import subprocess
import tempfile
import time
import zipfile
from pathlib import Path

import city_menu_playtest as base
from budget_catalog import references,decode_budget
from footer_catalog import source,decode
from hd_source_audit import sha,scene


def main():
    root=base.root
    rom=Path('/orig/RS201.ROM').read_bytes()
    footer,budget=source(rom),references(rom)
    samples=[]
    managed=os.environ.get('TAIPEI_POWER_MANAGED_BUDGET','0')=='1'
    target_tax=int(os.environ.get('TAIPEI_POWER_TARGET_TAX','99'))
    target_funds=int(os.environ.get('TAIPEI_POWER_TARGET_FUNDS','120000'))
    sample_limit=int(os.environ.get('TAIPEI_POWER_FUNDING_SAMPLES') or ('240' if managed else '120'))
    step_batch=int(os.environ.get('TAIPEI_POWER_STEPS_PER_UPDATE','400000'))
    receipt_updates=int(os.environ.get('TAIPEI_POWER_RECEIPT_UPDATES','60'))
    assert 0<=target_tax<=99 and 100000<=target_funds<=120000 and 1<=sample_limit<=480
    assert step_batch in [400000,2000000] and receipt_updates in [6,60]
    budget_actions=[]
    saves=Path(tempfile.mkdtemp(prefix='power-funding-saves.',dir='/workspace/runs'))

    def model():
        with zipfile.ZipFile(root/'capture.zip') as z:
            s,frame=json.loads(z.read('status.json')),z.read('frame-index.bin')
        assert sha(frame)==s['frame_index_sha256']
        return s,frame

    def key(label,value):
        before=base.status()
        base.action(label,value,acknowledge=True)
        assert len(base.status()['key_reads'])==len(before['key_reads'])+1,label

    def budget_keys(label,value,count):
        # 相同正常鍵盤輸入分批送入，只縮減逐鍵完整截圖。
        # 原版讀鍵與前端 make/break 仍逐筆核對，不改 steps/update 或時鐘。
        word,release={'Left':(0x4b00,0xcb),'Right':(0x4d00,0xcd)}[value]
        released=lambda s:sum(i.get('kind')=='keyboard' and i.get('scan')==release for i in s['inputs'])
        reads=[]
        for start in range(0,count,8):
            n=min(8,count-start)
            before=base.status()
            for _ in range(n):
                subprocess.run(['xdotool','keydown',value],check=True)
                try:time.sleep(.2)
                finally:subprocess.run(['xdotool','keyup',value],check=True)
                time.sleep(.2)
            base.wait_for(lambda s:len(s.get('key_reads') or [])>=len(before['key_reads'])+n,f'{label}-{start}-read',seconds=180)
            base.wait_for(lambda s:released(s)>=released(before)+n,f'{label}-{start}-release',seconds=180)
            after=base.status()
            actual=after['key_reads'][len(before['key_reads']):]
            assert len(actual)==n and all(r['Word']==word for r in actual),(label,start,len(actual))
            assert released(after)==released(before)+n
            reads.extend(actual)
        base.capture(label)
        return reads

    with (root/'app.log').open('w') as log:
        game=subprocess.Popen(['/workspace/runs/taipei-preview','-original','/orig','-saves',str(saves),
            '-receipts',str(root),'-mute','-steps-per-update',str(step_batch),
            '-receipt-every-updates',str(receipt_updates),'-materials',
            '/workspace/prototypes/hd-style','-theme','original','-stop-file',str(root/'stop')],
            stdout=log,stderr=subprocess.STDOUT)
        try:
            base.wait_for(lambda s:s.get('steps',0)>=700_000_000,'intro',progress=True)
            subprocess.run(['xdotool','search','--name','模擬台北','windowfocus'],check=True)
            base.action('intro-space','space')
            base.wait_for(lambda s:s.get('steps',0)>=800_000_000,'intro-wait')
            base.action('main','space')
            base.wait_for(lambda s:s.get('frame_index_sha256')=='5442a8135d36552561f03a46fc443978a76989979e0c25dc016027229b24dda4','main-ready')
            key('scenario-choice','Right')
            key('scenario-open','space')
            for i,value in enumerate(['space','space','space','0']):key(f'scenario-step-{i}',value)
            initial,frame=model()
            assert scene(initial,frame) and int(decode(frame,footer,1)[2])==77413
            assert any(f.get('Name','').lower()=='disa1.dsa' and f.get('Op')=='read' for f in initial['file_ops'])
            if managed:
                # 025 已證實 Left 增一／Right 減一。只經原版 owner 調整，
                # 每鍵重讀完整面板；實際停止值由來源記錄，不預設稅率邊界。
                key('funding-budget-menu','F3')
                key('funding-budget-open','space')
                current=decode_budget(model()[1],budget)
                assert current is not None and current['selected_rows']==[0]
                assert current['percent']==[10,100,100,100,100]
                for row,target,direction in [(0,target_tax,'Left')]+[(r,0,'Right') for r in range(1,5)]:
                    if row:key(f'funding-budget-row-{row}','Down')
                    current=decode_budget(model()[1],budget)
                    assert current is not None and current['selected_rows']==[row]
                    value=current['percent'][row]
                    count=abs(target-value)
                    reads=budget_keys(f'funding-budget-adjust-{row}',direction,count)
                    changed=decode_budget(model()[1],budget)
                    assert changed is not None and changed['selected_rows']==[row]
                    actual=changed['percent'][row]
                    assert all(changed['percent'][r]==current['percent'][r] for r in range(5) if r!=row)
                    assert value<=actual<=target if direction=='Left' else target<=actual<=value
                    budget_actions.append({'row':row,'key':direction,'before':value,'after':actual,
                        'target':target,'count':count,'original_reads':reads,'release_count':count,
                        'steps':base.status()['steps']})
                    current=changed
                base.capture('funding-managed-budget')
                key('funding-budget-return','Escape')
                assert scene(*model())
            key('funding-resume','3')
            funded=False
            for i in range(sample_limit):
                step=base.status()['steps']
                base.wait_for(lambda s:s.get('steps',0)>=step+24_000_000,f'funding-{i:03d}')
                s,frame=model()
                base.capture(f'funding-{i:03d}')
                panel=decode_budget(frame,budget)
                text=decode(frame,footer,1) if scene(s,frame) else None
                money=int(text[2]) if text is not None else None
                samples.append({'receipt':f'funding-{i:03d}-capture.zip','steps':s['steps'],
                    'year_month_funds':text,'funds':money,'annual_budget':panel})
                if panel is not None and s['dos_blocked']:
                    key(f'funding-budget-{i:03d}-return','Escape')
                elif panel is not None:
                    # 012 已實見年度預算自動計算時 BIOS 未阻塞，後續自行返回城市。
                    # 只觀察此相位；不向尚未等鍵的 owner 插入 Escape。
                    continue
                elif money is not None and money>=target_funds:
                    key('funding-pause','0')
                    funded=True
                    break
            saved_sha=None
            actual_money=None
            if funded:
                s,frame=model()
                actual_money=int(decode(frame,footer,1)[2])
                assert actual_money>=target_funds
                key('funding-file-menu','F2')
                key('funding-save-dialog','space')
                for i,value in enumerate('0001'):key(f'funding-save-name-{i}',value)
                key('funding-save-accept','space')
                saved=saves/'0001.SAV'
                assert saved.is_file() and saved.stat().st_size==93567
                saved_sha=sha(saved.read_bytes())
                key('funding-exit-menu','F1')
                key('funding-exit-select','Down')
                key('funding-exit-confirm','space')
                subprocess.run(['xdotool','type','--delay','150','Y'],check=True)
                base.wait_for(lambda s:s.get('dos_blocked') and any(k.get('Via')=='int21-AH07' and k.get('Key')==89 for k in s.get('key_reads',[])),'funding-score',seconds=180)
                base.capture('funding-score')
                key('funding-score-space','space')
                base.wait_for(lambda s:s.get('dos_exited'),'funding-native-exit',seconds=180)
                base.capture('funding-native-exit')
                assert game.wait(timeout=10)==0
            (root/'result.json').write_text(json.dumps({'issue':46,'normal_gui':True,'checkpoint':False,
                'funded':funded,'funds':actual_money,'samples':samples,'save_dir':str(saves),
                'managed_budget':managed,'budget_actions':budget_actions,
                'target_tax':target_tax,'target_funds':target_funds,'sample_limit':sample_limit,
                'steps_per_update':step_batch,'receipt_every_updates':receipt_updates,
                'save_sha256':saved_sha,'native_exit':bool(base.status().get('dos_exited')),
                'ordinary_acknowledgments':base.ordinary_sync,'arrow_acknowledgments':base.sync,
                'scope':'原版正常城市／速度 3／原版預算操作及存檔；不注入資金或改寫資料。核能施工及 HD 另驗'},ensure_ascii=False,indent=2)+'\n')
        finally:
            if game.poll() is None:
                (root/'stop').write_text('stop\n')
                try:game.wait(timeout=10)
                except subprocess.TimeoutExpired:game.kill();game.wait()
            assert game.returncode==0,game.returncode


if __name__=='__main__':main()
