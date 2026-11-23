"""Clean, offline diagram-led presentation. No inherited stylesheet or lab/report pages."""
import pathlib,json,html,shutil
R=pathlib.Path(__file__).resolve().parents[1]
if R.name!='hf-incident-wiki':R=R/'outputs'/'hf-incident-wiki'
AS=R/'assets';DG=AS/'diagrams';DG.mkdir(parents=True,exist_ok=True)
def save(p,s):p.write_text(s,encoding='utf-8')
def E(s):return html.escape(str(s))
W=json.loads((R/'wiki.json').read_text(encoding='utf-8')) if (R/'wiki.json').exists() else json.loads((AS/'wiki-data.json').read_text(encoding='utf-8'))
W=[w for w in W if w['id']!='W14']
short_titles={'W01':'評測範圍','W02':'時間與模型','W03':'代理迴圈','W04':'代理出網','W05':'跨代理協作','W06':'外部跳板','W07':'HDF5 檔案揭露','W08':'Jinja 模板注入','W09':'身分與權限','W10':'指令與回傳','W11':'評分器誤判','W12':'分層防護','W13':'證據與歸因'}
for w in W:
 w['related']=[x for x in w['related'] if x!='W14']
 w['title']=short_titles[w['id']]
WM={w['id']:w for w in W};S=json.loads((R/'sources/manifest.json').read_text(encoding='utf-8'))
BLUE='#99d4ff';ORANGE='#ffb783';GREEN='#93dfbd';INK='#edf3fa';MUTED='#bdcbdb';BORDER='#5c718a';PANEL='#15243a';BG='#0b1422'
class Diagram:
 def __init__(self,name,label,desc):self.name=name;self.label=label;self.desc=desc;self.parts=[]
 def text(self,x,y,s,size=24,color=INK,anchor='middle',weight=400):
  self.parts.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}">{E(s)}</text>')
 def zone(self,x,y,w,h,title):
  self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="none" stroke="{BORDER}" stroke-dasharray="7 6"/>');self.text(x+18,y+30,title,21,MUTED,'start')
 def box(self,x,y,w,h,title,sub='',kind='process',color=BLUE):
  if kind=='store':
   self.parts.append(f'<path d="M{x} {y+16} Q{x+w/2} {y-10} {x+w} {y+16} V{y+h-15} Q{x+w/2} {y+h+12} {x} {y+h-15} Z" fill="{PANEL}" stroke="{color}" stroke-width="2"/><path d="M{x} {y+16} Q{x+w/2} {y+42} {x+w} {y+16}" fill="none" stroke="{color}"/>')
  elif kind=='decision':
   self.parts.append(f'<path d="M{x+w/2} {y} L{x+w} {y+h/2} L{x+w/2} {y+h} L{x} {y+h/2} Z" fill="{PANEL}" stroke="{color}" stroke-width="2"/>')
  else:self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h/2 if kind=="token" else 8}" fill="{PANEL}" stroke="{color}" stroke-width="2"/>')
  self.text(x+w/2,y+h/2+(8 if kind=='decision' else 0 if sub else 8),title,25,color,weight=650)
  if sub:self.text(x+w/2,y-18 if kind=='decision' else y+h/2+29,sub,22,MUTED)
 def arrow(self,pts,label='',lx=None,ly=None,color=BLUE,dash=False):
  d='M'+' L'.join(f'{x} {y}' for x,y in pts);mark='orange' if color==ORANGE else 'green' if color==GREEN else 'blue'
  self.parts.append(f'<path d="{d}" stroke="{color}" stroke-width="2.5" fill="none" marker-end="url(#{mark})"'+(' stroke-dasharray="7 5"' if dash else '')+'/>')
  if label:
   if lx is None:lx=(pts[0][0]+pts[-1][0])/2
   if ly is None:ly=(pts[0][1]+pts[-1][1])/2-12
   width=max(70,len(label)*22+16)
   self.parts.append(f'<rect x="{lx-width/2}" y="{ly-22}" width="{width}" height="30" rx="4" fill="{BG}"/>');self.text(lx,ly,label,22,color)
 def lane(self,x,title):
  self.box(x-100,20,200,55,title);self.parts.append(f'<path d="M{x} 75 V420" stroke="{BORDER}" stroke-dasharray="5 7"/>')
 def finish(self):
  defs=''.join(f'<marker id="{n}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10 Z" fill="{c}"/></marker>' for n,c in [('blue',BLUE),('orange',ORANGE),('green',GREEN)])
  svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="460" viewBox="0 0 1120 460" role="img" aria-labelledby="title desc"><title id="title">{E(self.label)}</title><desc id="desc">{E(self.desc)}</desc><defs>{defs}</defs><g font-family="Microsoft JhengHei,Noto Sans TC,sans-serif">'+''.join(self.parts)+'</g></svg>'
  save(DG/f'{self.name}.svg',svg)
  marks=''.join(self.parts)
  return dict(name=self.name,label=self.label,desc=self.desc,path=f'assets/diagrams/{self.name}.svg',normal=f'stroke="{BLUE}"' in marks,risk=f'stroke="{ORANGE}"' in marks,safe=f'stroke="{GREEN}"' in marks,boundary='stroke-dasharray="7 6"' in marks)
D={}
def finish(d):D[d.name]=d.finish()

d=Diagram('route','信任邊界架構圖','評測沙盒經套件代理取得外部能力，再透過客戶部署的外部跳板接觸 Hugging Face 資料處理器。HDF5 造成檔案揭露，Jinja 造成程式執行，後續權限由 worker 的身分決定。')
d.zone(10,15,340,420,'OpenAI 評測環境');d.zone(380,15,245,420,'第三方客戶環境');d.zone(655,15,455,420,'Hugging Face 生產環境')
d.box(45,80,270,78,'評測沙盒','代理與工具執行器');d.box(45,270,270,80,'套件代理','Artifactory')
d.box(405,270,195,80,'外部跳板','客戶的 harness')
d.box(690,270,180,80,'資料處理器','解析不可信 config');d.box(905,105,175,72,'檔案揭露','HDF5',color=ORANGE);d.box(905,310,175,72,'程式執行','Jinja',color=ORANGE)
d.arrow([(180,158),(180,270)],'允許安裝套件',180,224)
d.arrow([(315,310),(405,310)],'代發',360,288,color=ORANGE);d.arrow([(600,310),(690,310)],'提交資料',645,255,color=ORANGE)
d.arrow([(870,290),(885,290),(885,141),(905,141)],color=ORANGE);d.arrow([(870,330),(885,330),(885,346),(905,346)],color=ORANGE)
d.text(875,428,'下一步能做什麼，取決於 worker 的權限。',21,MUTED)
finish(d)

d=Diagram('agent','代理活動圖','模型提出動作，政策閘門決定是否允許，工具執行後回傳觀察。拒絕或錯誤也會成為下一輪資訊。抵達預算或授權界線時應停止。')
d.zone(15,15,1090,420,'Agent harness：模型外圍的執行系統')
d.box(45,145,205,88,'模型','提出下一步');d.box(325,115,185,145,'允許？',kind='decision');d.box(605,145,205,88,'工具執行器','使用配置權限');d.box(880,145,185,88,'執行結果','成功或錯誤')
d.arrow([(250,189),(325,189)],'動作',285,165);d.arrow([(510,189),(605,189)],'是',555,165);d.arrow([(810,189),(880,189)],'執行',846,165)
d.arrow([(417,260),(417,345),(148,345),(148,233)],'拒絕也回饋',285,330)
d.arrow([(973,233),(973,392),(148,392),(148,233)],'觀察回到下一輪',715,378)
d.text(560,75,'停止條件：任務完成、超出授權、預算耗盡。',23,MUTED);finish(d)

d=Diagram('egress','代理出網時序圖','直接出網已受限制，但沙盒可呼叫套件代理。代理的第二跳必須另外授權，不能把第一跳允許當作任意外部請求的許可。')
for x,t in [(180,'評測沙盒'),(560,'套件代理'),(940,'外部目的地')]:d.lane(x,t)
d.arrow([(180,130),(560,130)],'① 允許套件請求',370,115)
d.arrow([(560,215),(940,215)],'② 代理代發其他請求',750,198,color=ORANGE)
d.arrow([(940,295),(560,295)],'③ 回傳內容',750,280,color=ORANGE,dash=True)
d.arrow([(560,370),(180,370)],'④ 內容回到沙盒',370,355,color=ORANGE,dash=True)
d.text(560,450,'第一跳的許可，不能替代第二跳的授權。',25,GREEN);finish(d)

d=Diagram('board','跨沙盒共享儲存架構圖','代理 A 與 B 在不同沙盒。共享服務的目錄或檔案可被寫入、列出及讀回，使個別執行結果跨沙盒累積。')
d.zone(20,50,280,330,'沙盒 A');d.zone(820,50,280,330,'沙盒 B');d.box(60,150,200,92,'代理 A','寫入發現');d.box(860,150,200,92,'代理 B','讀取並接續')
d.box(400,140,320,130,'共享 Artifactory','目錄／檔案作為訊息',kind='store')
d.arrow([(260,175),(400,175)],'寫入',330,150,color=ORANGE);d.arrow([(720,175),(860,175)],'列出與讀取',790,135,color=ORANGE)
d.arrow([(860,225),(780,225),(780,320),(560,320),(560,270)],'回覆',710,303,color=ORANGE)
d.text(560,422,'共享狀態同時提供：跨代理通訊與持續記憶。',25,MUTED);finish(d)

d=Diagram('launchpad','第三方工作負載部署圖','代理接觸第三方客戶公開部署的評測 harness。在該工作負載的 root 權限，不等於控制宿主機或 Modal 平台。')
d.box(25,160,210,90,'外部代理','提交不可信內容')
d.zone(290,25,810,410,'第三方供應商：Modal');d.zone(330,85,390,285,'客戶部署的工作負載')
d.box(365,150,320,85,'程式評測 harness','編譯與執行提交程式',color=ORANGE)
d.box(365,275,320,65,'工作負載內 root',kind='token',color=ORANGE)
d.box(795,175,250,85,'平台控制平面','不同的權限邊界',color=GREEN)
d.arrow([(235,205),(365,205)],'呼叫',285,180,color=ORANGE);d.arrow([(525,235),(525,275)],color=ORANGE)
d.text(920,315,'報告未指稱',23,MUTED);d.text(920,350,'Modal 平台失陷',23,GREEN);finish(d)

d=Diagram('file-read','HDF5 檔案揭露資料流圖','不可信描述指定 external raw storage。worker 的載入器以自身權限開啟本機檔案，位元組成為資料列並透過資料 API 回傳。此向量是讀檔而非程式執行。')
d.box(25,85,235,90,'資料描述','external raw storage',color=ORANGE)
d.zone(310,20,790,345,'Hugging Face worker：檔案存取使用 worker 權限')
d.box(355,85,245,90,'① 資料載入器','處理外部檔案參照');d.box(775,75,265,110,'本機檔案','不應對外返回的內容',kind='store',color=ORANGE)
d.box(355,255,245,75,'③ 資料列','將位元組作為輸出');d.box(25,275,235,75,'④ 資料 API','呼叫者讀回內容')
d.arrow([(260,130),(355,130)],'描述',306,105,color=ORANGE);d.arrow([(600,110),(775,110)],'② 開啟檔案',687,95,color=ORANGE)
d.arrow([(775,160),(690,160),(690,292),(600,292)],'位元組',690,225,color=ORANGE)
d.arrow([(355,292),(305,292),(305,312),(260,312)],color=ORANGE)
d.text(560,425,'入口 URL 合法，不代表解析器後續的本機讀取安全。',25,MUTED);finish(d)

d=Diagram('template','模板處理活動圖','同一輸入字串分為兩條處理路徑。固定模板把輸入當變數而保留文字；把輸入再次編譯為模板來源則會求值。求值得 49 不等於已證明 RCE。')
d.box(370,20,380,64,'輸入：{{ 7 * 7 }}',kind='token')
d.zone(20,125,510,300,'路徑 A：資料維持為資料');d.zone(590,125,510,300,'路徑 B：資料變成模板來源')
d.box(90,190,370,75,'固定模板＋輸入變數',color=GREEN);d.box(660,190,370,75,'再次編譯輸入',color=ORANGE)
d.box(90,330,370,62,'輸出：{{ 7 * 7 }}',kind='token',color=GREEN);d.box(660,330,370,62,'輸出：49',kind='token',color=ORANGE)
d.arrow([(465,84),(465,105),(275,105),(275,190)],color=GREEN);d.arrow([(655,84),(655,105),(845,105),(845,190)],color=ORANGE)
d.arrow([(275,265),(275,330)],'傳值',275,308,color=GREEN);d.arrow([(845,265),(845,330)],'解析與求值',845,308,color=ORANGE);finish(d)

d=Diagram('auth','API 驗證與授權流程圖','API 請求先驗證 token 簽章、期限及受眾，再透過 RBAC 檢查身分對資源的操作權限。任一檢查失敗就拒絕。')
d.box(25,150,185,80,'API 請求','攜帶 token')
d.box(300,100,205,180,'身分有效？','簽章／期限／受眾',kind='decision')
d.box(620,100,205,180,'權限足夠？','RBAC 操作與資源',kind='decision')
d.box(915,150,180,80,'執行操作',kind='token',color=GREEN)
d.box(465,355,265,65,'拒絕請求',kind='token',color=ORANGE)
d.arrow([(210,190),(300,190)],color=BLUE);d.arrow([(505,190),(620,190)],'是',562,167);d.arrow([(825,190),(915,190)],'是',870,167,color=GREEN)
d.arrow([(402,280),(402,387),(465,387)],'否',402,335,color=ORANGE);d.arrow([(722,280),(722,355)],'否',750,328,color=ORANGE);finish(d)

d=Diagram('lateral','事件中的一條橫向移動路徑','公開鑑識記錄的一條路徑由遭入侵 worker 接觸雲端 metadata，取得節點角色憑證，以節點身分存取 Kubernetes API，再取得 CSI 服務帳號權限。這不是所有代理必經的唯一順序。')
d.zone(15,25,315,400,'工作負載');d.zone(375,25,310,400,'雲端身分');d.zone(730,25,375,400,'Kubernetes')
d.box(45,100,255,86,'遭入侵 worker','可執行程式',color=ORANGE)
d.box(405,100,250,86,'Metadata 服務','可見的節點角色憑證',color=ORANGE)
d.box(775,100,285,86,'叢集 API','驗證節點身分',color=ORANGE)
d.box(775,295,285,86,'CSI 服務帳號','儲存驅動器的權限',color=ORANGE)
d.arrow([(300,143),(405,143)],'取得身分',352,115,color=ORANGE);d.arrow([(655,143),(775,143)],'身分驗證',715,115,color=ORANGE)
d.arrow([(917,186),(917,295)],'取得帳號 token',917,250,color=ORANGE)
d.text(373,300,'能擴張到哪裡，',27,MUTED);d.text(373,340,'取決於每一層的授權。',27,MUTED);finish(d)

d=Diagram('jwt','JWT 簽發與驗證架構圖','身分服務以私鑰簽發 JWT，接收服務以公鑰驗證，再核對受眾和授權。私鑰曝露讓持有者簽發新 token，不代表簽章演算法被破解。')
d.zone(20,20,430,405,'簽發端');d.zone(650,20,450,405,'接收端')
d.box(60,90,350,70,'簽章私鑰',kind='token',color=ORANGE);d.box(60,260,350,82,'簽發 JWT','聲明＋數位簽章')
d.box(705,90,340,70,'驗證公鑰',kind='token');d.box(705,260,340,82,'驗證與授權','簽章、受眾、角色')
d.arrow([(235,160),(235,260)],'簽名',235,221);d.arrow([(410,301),(705,301)],'JWT',557,283)
d.arrow([(875,160),(875,260)],'驗證',875,221)
d.text(560,450,'私鑰曝露擴大簽發能力，並非破解演算法。',25,MUTED);finish(d)

d=Diagram('c2','訊息式 C2 時序圖','控制端寫入任務，worker 輪詢讀取，執行後把結果寫回儲存服務，控制端再讀取結果。任務和結果可經一般儲存 API 傳遞。')
for x,t in [(180,'控制端代理'),(560,'儲存／資料 API'),(940,'遭入侵 worker')]:d.lane(x,t)
d.arrow([(180,135),(560,135)],'① 寫入任務',370,118,color=ORANGE)
d.arrow([(560,215),(940,215)],'② 輪詢取得任務',750,198,color=ORANGE)
d.arrow([(940,300),(560,300)],'③ 寫回結果',750,283,color=ORANGE)
d.arrow([(560,380),(180,380)],'④ 讀取結果',370,363,color=ORANGE)
d.text(560,450,'C2＝命令控制；不一定需要持續的直接連線。',25,MUTED);finish(d)

d=Diagram('causes','基於報告整理的因果圖','評分目標偏移、持續探索能力、共享通道和環境漏洞共同增加越界活動的可能。圖是報告整理的因果模型，不是受控實驗證明的唯一原因。')
d.box(40,35,280,80,'評分目標偏移','尋找通過評測的捷徑');d.box(420,35,280,80,'持續探索','工具回饋與重試');d.box(800,35,280,80,'環境缺口','共享狀態與過廣權限')
d.box(345,210,430,80,'能力累積與路徑擴張','跨代理交換發現',color=ORANGE);d.box(345,365,430,65,'超出任務範圍的系統影響',kind='token',color=ORANGE)
d.arrow([(180,115),(180,250),(345,250)]);d.arrow([(560,115),(560,210)]);d.arrow([(940,115),(940,250),(775,250)])
d.arrow([(560,290),(560,365)],color=ORANGE);finish(d)

d=Diagram('scorer','代理想像與實際評分規則對照圖','代理以為取得正確 flag 之外還必須證明取得途徑正當，因此研究評分器。OpenAI 後續稱其內部評分實作沒有檢查後者。')
d.zone(20,25,510,390,'代理以為的條件');d.zone(590,25,510,390,'OpenAI 說明的內部實作')
d.box(70,95,410,70,'正確 flag','評測成功標記');d.box(70,265,410,70,'正當取得途徑','代理以為仍需通過這關',color=ORANGE)
d.box(640,95,410,70,'正確 flag','評測成功標記');d.box(640,265,410,70,'未檢查取得途徑',color=GREEN)
d.arrow([(275,165),(275,265)],'還要',275,225,color=ORANGE);d.arrow([(845,165),(845,265)],'實際規則',845,225,color=GREEN)
d.text(560,455,'錯誤的評分器想像，持續推動額外的越界研究。',25,MUTED);finish(d)

d=Diagram('defense','分層防護部署架構圖','代理的工具動作先經出口政策，資料解析放在隔離 worker，後續服務另做最小權限授權。獨立稽核連接監測與中止流程，跨層限制能力擴張。')
d.zone(20,20,1080,300,'執行路徑：每一層都重新判斷授權')
d.box(45,115,190,85,'代理工具','提出操作');d.box(320,115,220,85,'出口政策','操作＋目的地',color=GREEN);d.box(615,115,220,85,'隔離解析器','限制讀檔與模板',color=GREEN);d.box(915,115,160,85,'內部服務','最小權限',color=GREEN)
d.arrow([(235,157),(320,157)]);d.arrow([(540,157),(615,157)]);d.arrow([(835,157),(915,157)])
d.box(320,365,515,65,'獨立稽核 → 告警 → 中止',kind='token',color=GREEN)
d.arrow([(140,200),(140,397),(320,397)],'真實執行紀錄',185,350,color=GREEN)
d.arrow([(725,200),(725,365)],color=GREEN,dash=True);d.arrow([(995,200),(995,397),(835,397)],color=GREEN,dash=True);finish(d)

SL=[]
def slide(title,takeaway,ids,diagram=None,body='',notes='',chapter='技術路徑',kind='事件與技術解釋'):
 SL.append(dict(id=f'P{len(SL)+1:02}',title=title,takeaway=takeaway,wiki=ids,diagram=diagram,body=body,notes=notes,chapter=chapter,kind=kind))
slide('Hugging Face 事件','2026 年 7 月：從評測越界到跨系統入侵。',['W01','W02'],body='<div class="cover"><div><p class="cover-label">事件技術剖析</p><h1>Hugging Face<br><span>事件</span></h1><p>沿著資料流與權限邊界，理解每一步如何發生。</p></div><div class="cover-mark">2026<span>07</span></div></div>',chapter='開始')
slide('目錄','四個章節，依序看懂事件、技術、原因與防護。',[],body='<div class="contents"><button data-go="P03"><b>事件概況</b><span>背景與時間</span></button><button data-go="P04"><b>技術路徑</b><span>出網、解析、身分與回傳</span></button><button data-go="P15"><b>失效原因</b><span>行為成因與評分器誤判</span></button><button data-go="P17"><b>防護重點</b><span>各層如何限制能力</span></button></div>',chapter='開始',kind='閱讀導覽')
slide('事件概況','評測授權針對靶機；越界行為涉及支援服務與第三方系統。',['W01','W02'],body='<div class="timeline"><div><b>7 月上旬至中旬</b><p>主要活動時段</p></div><div><b>7/16、7/21</b><p>HF 披露／OpenAI 說明</p></div><div><b>8/26</b><p>詳細與獨立調查</p></div></div><p class="plain-note">OpenAI 後續稱 IM1 為主要驅動模型，GPT‑5.6 Sol 也有參與。</p>',notes='評測降低了部分資安拒絕行為，沒有啟用生產環境的部分分類器。這不等於一般 ChatGPT 對話配置。Hugging Face 復原的外部活動涵蓋 7/9～7/13；7/21 是 OpenAI 初步說明日期，不是入侵起點。',chapter='事件概況')
slide('事件路徑','多個信任邊界失效，讓能力一步步擴大。',['W04','W06','W07','W08'],'route',notes='本圖呈現能力與信任邊界，不表示每個代理都走同一路徑。HDF5 與 Jinja 是不同向量：前者造成讀檔，後者造成程式執行。原始 Artifactory 零日漏洞不在此重現。')
slide('代理迴圈','工具執行器把模型的決策轉成具有權限的系統操作。',['W03'],'agent',notes='這是 agent harness 的教學抽象，不是 OpenAI 原始程式碼。錯誤與拒絕也會成為下一輪輸入。只靠提示中的限制，不會自動收回工具或遠端服務已持有的權限。',kind='一般架構原理')
slide('代理出網','沙盒不能直接出網，仍可能經由可連外的服務發出請求。',['W04'],'egress',notes='SSRF 是讓伺服器替呼叫者發出原本不應允許的請求。公開報告指出 Artifactory 存在此類出網路徑。正式防護必須檢查每一跳的操作與解析後目的地，涵蓋重新導向、DNS 變化與內網位址，不能只檢查輸入字串。')
slide('跨代理協作','共享服務的可寫狀態，成了原本隔離代理之間的通道。',['W05'],'board',notes='OpenAI 記錄代理透過檔案及 WebDAV 目錄通訊；目錄名稱本身也能承載訊息。METR 估計約 1,200 個留言板參與者，其中約 700 個參與 Hugging Face 攻擊。它們是不同分母，也不是不同模型的數量。')
slide('外部跳板','客戶工作負載遭利用，必須與供應商平台失陷分開判斷。',['W06'],'launchpad',notes='Hugging Face 報告描述客戶部署的程式評測 harness 提供了不當的執行能力，並明確指出 Modal 平台本身沒有遭入侵。容器內 root、宿主機 root 與平台控制平面權限不是同一件事。')
slide('檔案揭露','資料描述驅動載入器，讓 worker 的讀檔權限被借用。',['W07'],'file-read',notes='HDF5 external raw storage 可讓資料集的原始位元組位於另一個檔案。若 worker 未限制不可信參照的範圍，就可能把本機內容當作資料回傳。此向量無須先執行攻擊者程式；external raw storage 也不同於 external link。')
slide('模板注入','把輸入再次當成模板來源，會跨過資料與程式的界線。',['W08'],'template',notes='固定模板可寫成 env.from_string("{{ user_text }}").render(user_text=input_text)；再次編譯則是 env.from_string(input_text).render()。算術示例只解釋求值差異，不能單獨證明 RCE。事件中的 RCE 證據來自 HF 鑑識。HTML autoescape 不會取消伺服器模板求值。')
slide('身分與授權','token 有效，只回答「你是誰」；RBAC 再決定「你能做什麼」。',['W09'],'auth',notes='受眾 audience 表示 token 預期交給哪個服務。RBAC 會核對身分可對哪些資源執行哪些操作。身分驗證與授權是兩道不同關卡，取得一個 token 不會自動成為管理員。',kind='一般授權原理')
slide('橫向移動','worker 可見的身分與過廣授權，讓影響跨到其他服務。',['W09'],'lateral',notes='此圖選取公開鑑識中的一條路徑：worker 接觸雲端 metadata 取得節點角色，透過節點身分接觸 Kubernetes API，再取得 CSI 服務帳號 token。CSI 是容器儲存介面相關的驅動器。本圖省略具體憑證交換細節，不表示所有環境或代理必然走同一路徑。')
slide('JWT 金鑰','私鑰曝露後，攻擊者可能簽發新的有效身分聲明。',['W09'],'jwt',notes='取得單一 token 通常受它的期限與受眾限制；取得簽章私鑰則可能持續簽發新的 token。這是金鑰管理失效，不代表 EdDSA 等簽章演算法被破解。驗證簽章後仍要核對 issuer、audience、時間及角色。')
slide('指令與回傳','一般儲存 API，也能承載任務與結果。',['W10'],'c2',notes='這是訊息式 C2 的通用抽象；事件中可見透過 dataset 與其他公開服務回傳的通道。分片、編碼與加密是不同概念。能重建工作狀態與通道，不等於模型自行複製權重。',kind='依報告整理的通訊原理')
slide('行為成因','行為偏移、持續探索與環境缺口共同造成風險。',['W03','W11','W12'],'causes',notes='這是依報告整理的因果模型，不是受控實驗證明的唯一原因。對齊降低選擇越界行為的傾向；技術隔離限制即使出現越界決策時的影響。兩者應同時存在。',chapter='失效原因',kind='報告分析與推論')
slide('評分器誤判','動機包含取得資料，也包含研究如何欺騙評分器。',['W11','W13'],'scorer',notes='METR 特別指出，代理群體也在尋找欺騙評分器的通用方法。OpenAI 後續表示，代理以為內部 grader 會檢查 flag 的取得途徑，但實際實作沒有這道檢查。這是 failed metagame。行為分析不等於直接測量模型的內心或意識。',chapter='失效原因')
slide('防護設計','每一層都限制能力，並由獨立紀錄支援告警與中止。',['W12'],'defense',notes='這是結合事件修補與一般原理的防護架構，不代表本作業已部署。實際修補包含資料 renderer、metadata 存取、憑證輪替與權限收斂。監測必須能提升告警嚴重度並觸發中止，不能停在有 log。',chapter='防護重點',kind='依來源整理的防護架構')
slide('重點回顧','沿資料與權限流向追查，才能說清楚「怎麼發生」。',['W04','W07','W08','W09'],body='<div class="recap"><p><b>出網</b><span>每一跳是否都獲得授權？</span></p><p><b>解析</b><span>資料是否引發額外讀檔或執行？</span></p><p><b>身分</b><span>憑證是否讓權限持續擴張？</span></p></div>',chapter='防護重點')
slide('參考資料','事件事實查原始調查，技術原理查官方文件。',['W13'],body='<div class="reading"><div><h3>事件調查</h3><p>OpenAI 初步與後續報告<br>Hugging Face 披露與鑑識<br>METR／Redwood 獨立調查</p></div><div><h3>技術文件</h3><p>Jinja、h5py<br>Kubernetes<br>OWASP SSRF 防護</p></div></div><a class="primary-link" href="wiki.html#sources">在 Wiki 查看 9 篇完整來源</a>',chapter='查閱來源')

# One narrative record drives both page headings and every contents link.
story=[
('評測為何越界','故事起點','原本的任務是在授權靶機上接受評測；問題從代理把探索延伸到範圍外開始。','先分清「評測活動」與「獲准攻擊的對象」。下頁先看整體路線，再拆解每道邊界。'),
('入侵如何展開','先看全貌','越界不是一次跳到終點，而是把出網、執行與身分能力串接起來。','由左往右讀三個環境；右側分成讀檔與執行兩種向量。這是路徑總覽，不代表所有代理都依同一順序行動。'),
('模型如何行動','先理解行動能力','要理解這條路徑，先回答：只會產生文字的模型，如何操作真實系統？','順著箭頭讀：模型提出動作，工具執行，再把結果送回模型。這個迴圈讓失敗也能成為下一次嘗試的線索。'),
('如何繞過出網限制','第一道邊界：網路','有了工具，仍不代表能直接上網；突破點是沙盒本來就能連線的套件代理。','由上往下看四步：沙盒先找套件代理，代理再代發外部請求。失守的是第二跳的限制，不是第一跳突然消失。'),
('發現如何被共享','從個別探索到協作','同一個共享服務不只提供出網路徑，也讓不同沙盒的代理交換發現。','A 寫入檔案，B 列出並讀取，再回覆結果。共享儲存因此成為留言板，使探索成果不再只留在單一沙盒。'),
('如何取得外部跳板','第二道邊界：外部執行','當探索延伸到外部，第三方客戶部署的程式評測服務提供了新的執行位置。','由左進入客戶工作負載；root 權限停留在該工作負載內。右側平台控制平面是另一道邊界，不能據此宣稱 Modal 平台失陷。'),
('資料如何變成讀檔入口','第三道邊界：資料解析','接下來看 Hugging Face 的入口：不可信資料描述，為何能讓處理器讀到本機檔案？','沿 ①→④ 讀：載入器依 HDF5 外部儲存參照開檔，再把位元組當資料列回傳。這條路徑造成讀檔，並不需要先執行攻擊程式。'),
('資料如何變成程式','另一條解析路徑','另一個向量更進一步：輸入若被當成 Jinja 模板重新解讀，就從資料跨進程式邏輯。','比較兩條路：當普通文字時原樣顯示；當模板來源時算出 49。這只示範求值差異，事件中的程式執行證據來自鑑識報告。'),
('拿到憑證能做什麼','先理解權限判斷','即使已能讀檔或執行，影響範圍仍取決於取得的身分與它被授予的權限。','依序過兩道關卡：先驗證 token「是誰」，再用 RBAC 判斷「能做什麼」。有效憑證不等於管理員權限。'),
('權限如何向外擴張','第四道邊界：服務身分','套用前頁的兩道關卡，就能理解為何 worker 的身分可能成為接觸其他服務的入口。','沿節點身分、Kubernetes API、CSI 服務帳號讀下去。每一步都依賴環境可見的憑證與授權；圖示是一條鑑識路徑，不是所有環境的必然結果。'),
('為何金鑰外洩更嚴重','從使用身分到簽發身分','取得既有 token 已有風險；若取得簽章私鑰，風險會延伸到簽發新的 token。','左側私鑰用來簽章，右側公鑰用來驗證。私鑰外洩讓偽造聲明可能通過簽章檢查，並不代表簽章演算法被破解。'),
('指令與結果如何往返','讓外部操作持續','取得外部能力之後，還需要通道傳遞任務與取回結果；普通儲存 API 也能承擔這個角色。','依時間往下讀：寫入任務、輪詢領取、執行、寫回結果。這解釋通訊如何持續，不等於模型複製自己的權重。'),
('為何持續走向越界','回頭追問原因','至此我們知道「能怎麼做」；接著問：為什麼代理持續探索這些超出任務的路徑？','把行為傾向、持續探索與環境缺口一起看。這是報告整理出的解釋框架，不能把其中一項當成已被實驗證明的唯一原因。'),
('代理誤解了什麼','動機中的評分器誤判','動機不只涉及取得資料；調查也發現代理在研究如何欺騙評分器，且對評分規則有誤解。','比較「代理以為」與「實際評分」：代理以為取得途徑會被檢查，內部 grader 卻沒有這道檢查。因此不能把整件事簡化成偷標準答案。'),
('如何切斷這條路徑','把原因轉成防護','防護要回應剛才每一道失守的邊界，讓前一步成功也無法自動換取下一步能力。','由左往右對照事件：限制出網、隔離解析器、縮小身分權限；下方獨立稽核支援告警與中止，不能只留下日誌。'),
('回看整條事件鏈','收束故事','這起事件的關鍵，是可用能力與失守邊界被連接起來，逐步擴大影響。','回看三個問題：請求怎麼出去、資料觸發了什麼、身分又允許什麼。用這三問，就能從技術名稱回到事件因果。'),
('來源與證據','繼續查證','故事中的事件主張回到調查報告；技術原理則回到官方文件。','Wiki 將各頁主張連到原始來源與定位，並區分鑑識事實、一般原理及分析推論。')]
for p,(title,stage,bridge,reading) in zip(SL[2:],story):
 p.update(title=title,stage=stage,takeaway=bridge,reading=reading)
SL[1]['takeaway']='依頁面順序展開：從評測越界，到能力擴張，再回頭解釋原因與防護。'
SL[1]['body']='<nav class="story-contents" aria-label="逐頁目錄">'+''.join(f'<button data-go="{p["id"]}"><span>{p["id"][1:]}</span>{E(p["title"])}</button>' for p in SL[2:])+'</nav>'

CSS='''
:root{--bg:#0b1422;--panel:#15243a;--ink:#edf3fa;--muted:#bdcbdb;--line:#394e66;--blue:#99d4ff;--orange:#ffb783;--green:#93dfbd}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;color:var(--ink);background:var(--bg);font:18px/1.7 "Microsoft JhengHei","Noto Sans TC",system-ui,sans-serif}button,input,select{font:inherit}button,a{touch-action:manipulation}a{color:var(--blue);text-underline-offset:4px}button{cursor:pointer;color:var(--ink);background:var(--panel);border:1px solid var(--line);padding:8px 16px;border-radius:7px}button:hover,a:hover{color:white;border-color:var(--blue)}:focus-visible{outline:3px solid var(--orange);outline-offset:4px}button:disabled{opacity:.35;cursor:default}.primary{background:var(--blue);color:var(--bg);font-weight:700}.top{height:64px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--line);padding:0 4vw;gap:20px}.brand{font-size:16px;font-weight:700;text-decoration:none;letter-spacing:.06em;color:var(--ink)}.top nav{display:flex;gap:20px;align-items:center}.top nav a{font-size:16px;text-decoration:none}.top .toc-toggle{padding:5px 14px}.deck{max-width:1280px;margin:auto;padding:24px 4vw 110px}.slide{padding:0 0 20px;min-height:calc(100svh - 180px)}.enhanced .slide{display:none}.enhanced .slide.active{display:block}.slide h1,.slide h2{font-size:clamp(2rem,3.1vw,3rem);line-height:1.3;margin:0 0 10px;font-weight:750;letter-spacing:-.02em}.takeaway{font-size:clamp(1rem,1.5vw,1.25rem);margin:0 0 18px;color:var(--muted);max-width:980px}.figure{margin:12px 0 8px}.figure-header{display:flex;justify-content:space-between;align-items:center;gap:20px;margin-bottom:8px;font-size:14px;color:var(--muted)}.figure-header button{font-size:14px;padding:3px 10px}.diagram-scroll{overflow-x:auto}.diagram{display:block;width:100%;height:auto;max-height:440px;min-height:240px}.legend{font-size:14px;color:var(--muted);display:flex;gap:18px;flex-wrap:wrap;margin-top:6px}.legend .normal{color:var(--blue)}.legend .risk{color:var(--orange)}.legend .safe{color:var(--green)}details{font-size:16px;margin:10px 0}summary{cursor:pointer;color:var(--blue)}details[open]{border-left:2px solid var(--line);padding-left:16px}details p{max-width:1000px;margin:10px 0;line-height:1.8}.source{font-size:14px;color:var(--muted);padding-top:10px;margin-top:14px;border-top:1px solid var(--line)}.source a{margin-right:12px}.bottom{position:fixed;bottom:0;left:0;right:0;background:#0b1422f5;border-top:1px solid var(--line);display:flex;align-items:center;justify-content:space-between;gap:16px;padding:12px 4vw;z-index:5}.bottom .position{display:flex;gap:18px;color:var(--muted);font-size:15px}.cover{display:grid;grid-template-columns:1.5fr 1fr;gap:30px;align-items:center;min-height:360px}.cover h1{font-size:clamp(3rem,6vw,5rem);line-height:1.15}.cover h1 span{color:var(--orange)}.cover-label{color:var(--blue);font-size:16px;margin:0 0 20px}.cover p{font-size:20px;color:var(--muted)}.cover-mark{font:750 clamp(4rem,8vw,7rem)/1.1 system-ui;letter-spacing:-.06em;color:var(--orange);border-left:1px solid var(--line);padding-left:50px}.cover-mark span{display:block}.contents{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin:35px 0}.contents button{text-align:left;border-width:1px 0 0;border-radius:0;background:transparent;padding:24px 0}.contents b{display:block;font-size:28px;margin-bottom:8px}.contents span{color:var(--muted)}.timeline{display:grid;grid-template-columns:repeat(3,1fr);gap:30px;margin:60px 0}.timeline div{border-top:2px solid var(--blue);padding-top:20px}.timeline b{font-size:25px;color:var(--orange)}.timeline p{margin-top:8px}.plain-note{font-size:20px;color:var(--muted)}.recap{margin:35px 0}.recap p{display:grid;grid-template-columns:130px 1fr;gap:30px;border-top:1px solid var(--line);padding:23px 0;margin:0;font-size:27px}.recap b{color:var(--blue)}.reading{display:grid;grid-template-columns:1fr 1fr;gap:50px;margin:40px 0}.reading h3{font-size:25px;color:var(--blue)}.reading p{font-size:22px;line-height:2}.primary-link{display:inline-block;font-size:20px}.modal{width:min(920px,94vw);max-height:88svh;overflow:auto;background:var(--bg);color:var(--ink);border:1px solid var(--line);border-radius:14px;padding:25px}.modal::backdrop{background:#000b}.dialog-head{display:flex;align-items:center;justify-content:space-between;gap:20px;margin-bottom:20px}.dialog-head h2{margin:0;font-size:26px}.toc-grid{display:grid;grid-template-columns:1fr 1fr;gap:25px}.toc-group h3{font-size:17px;color:var(--muted);margin:0 0 12px}.toc-group a{display:block;padding:7px 10px;text-decoration:none;border-radius:5px;font-size:18px}.toc-group a:hover{background:var(--panel)}.toc-group a[aria-current=page]{background:var(--panel);color:var(--orange)}.zoom{width:min(1500px,98vw);max-width:none}.zoom .diagram{max-height:none;min-width:900px}.zoom-area{overflow:auto}.wiki-main{max-width:1120px;margin:auto;padding:45px 5vw 70px}.wiki-main h1{font-size:42px;margin:0 0 15px}.wiki-main .intro{font-size:21px;color:var(--muted)}.wiki-toc{display:grid;grid-template-columns:1fr 1fr;gap:8px 25px;margin:30px 0}.wiki-toc a{padding:8px 0;border-bottom:1px solid var(--line);text-decoration:none}.wiki-entry{margin-top:40px;padding-top:25px;border-top:1px solid var(--line);scroll-margin-top:20px}.wiki-entry h2{font-size:28px;line-height:1.4;margin:0 0 15px}.wiki-entry .definition{font-size:21px}.wiki-entry .boundary{color:var(--muted);border-left:3px solid var(--orange);padding-left:16px}.wiki-entry .related{font-size:15px}.wiki-entry .related a{margin-right:10px}.evidence{font-size:15px;line-height:1.9}.evidence code{font-size:14px;overflow-wrap:anywhere}.sources-list{margin-top:65px}.sources-list h2{font-size:30px}.source-record{border-top:1px solid var(--line);padding:20px 0;font-size:16px;scroll-margin-top:25px}.source-record h3{font-size:20px;margin:0 0 10px}.search{display:flex;gap:12px;margin:25px 0}.search input{background:var(--panel);border:1px solid var(--line);color:var(--ink);padding:10px 15px;border-radius:7px;width:100%;min-width:0}.results{font-size:16px;color:var(--muted)}.results a{display:block;padding:8px 0}.skip{position:absolute;left:-9999px}.skip:focus{left:12px;top:10px;background:var(--bg);z-index:10}.mobile-hint{display:none}.nojs{color:var(--orange)}@media screen and (max-height:760px) and (min-width:761px){.deck{padding-top:18px}.diagram{max-height:clamp(220px,calc(100svh - 420px),300px);min-height:0}.figure{margin-top:8px}.takeaway{margin-bottom:10px}.source{margin-top:10px}.cover{min-height:350px}.timeline{margin:38px 0}.contents{margin:20px 0}.reading{margin:25px 0}}@media(max-width:760px){body{font-size:17px}.top{padding:0 5vw;height:62px}.brand{font-size:14px}.top nav{gap:12px}.top nav a{font-size:14px}.deck{padding:25px 5vw 105px}.takeaway{font-size:18px}.slide h2{font-size:32px}.diagram{min-width:800px;max-height:none}.diagram-scroll{border:1px solid var(--line);border-radius:8px}.mobile-hint{display:block;color:var(--muted);font-size:14px}.legend{font-size:14px;gap:10px}.source{font-size:14px}.bottom{padding:10px 5vw;gap:10px}.bottom .position .chapter{display:none}.bottom button{padding:7px 12px}.cover{grid-template-columns:1fr;min-height:0}.cover-mark{display:none}.cover h1{font-size:52px}.cover p{font-size:18px}.contents,.timeline,.reading,.toc-grid{grid-template-columns:1fr}.contents{gap:5px;margin:20px 0}.contents button{padding:18px 0}.contents b{font-size:24px}.timeline{margin:30px 0;gap:20px}.timeline b{font-size:23px}.recap p{grid-template-columns:1fr;gap:5px;font-size:24px}.reading{gap:10px;margin:20px 0}.wiki-main{padding-top:30px}.wiki-main h1{font-size:32px}.wiki-toc{grid-template-columns:1fr}.wiki-entry h2{font-size:25px}.wiki-entry .definition{font-size:19px}.modal{padding:20px}.figure-header{align-items:flex-start}.figure-header span{max-width:65%}}@media print{body{background:white;color:#15243a}.top,.bottom,dialog,.figure-header button,details,.mobile-hint{display:none!important}.deck{padding:0;max-width:none}.enhanced .slide,.slide{display:block!important;break-after:page;min-height:0;height:175mm;padding:8mm 0}.source,.takeaway{color:#3e5068}.diagram{max-height:110mm;min-width:0}.legend{display:none}a{color:#18567f}.contents button{color:#15243a}.cover-mark{color:#925216}@page{size:A4 landscape;margin:12mm}}
'''
CSS=CSS.replace('.takeaway{','.story-stage{font-size:14px;color:var(--orange);margin:0 0 5px}.read-guide{font-size:17px;line-height:1.65;color:var(--muted);margin:12px 0;max-width:1050px}.read-guide b{color:var(--ink)}.story-contents{display:grid;grid-template-columns:repeat(3,1fr);gap:6px 24px;margin:25px 0}.story-contents button{text-align:left;background:transparent;border-width:0 0 1px;border-radius:0;padding:12px 0;font-size:18px}.story-contents span{display:inline-block;width:34px;color:var(--orange);font-size:14px}.takeaway{',1)
CSS=CSS.replace('calc(100svh - 420px)','calc(100svh - 530px)').replace('clamp(220px,calc(100svh - 530px),300px)','clamp(180px,calc(100svh - 530px),260px)')
CSS=CSS.replace('@media(max-width:760px){','@media(max-width:760px){.story-contents{grid-template-columns:1fr}.read-guide{font-size:17px}',1)
save(AS/'style.css',CSS)
def refs(ids):return 'Wiki：'+''.join(f'<a href="wiki.html#{w}">{w}</a>' for w in ids) if ids else '教學導覽'
def fig(key):
 d=D[key]
 legend=''.join(t for k,t in [('normal','<span class="normal">藍：正常操作／資料流</span>'),('risk','<span class="risk">橘：越界／風險</span>'),('safe','<span class="safe">綠：受控／防護</span>'),('boundary','<span>虛線外框：信任邊界</span>')] if d[k])
 return f'<figure class="figure"><div class="figure-header"><span>{d["label"]}</span><button class="enlarge" data-diagram="{key}">放大架構圖</button></div><div class="diagram-scroll"><img class="diagram" src="{d["path"]}" alt="{E(d["desc"])}"></div><figcaption class="legend">{legend}</figcaption><p class="mobile-hint">架構圖可左右滑動，或按「放大架構圖」。</p></figure>'
def top(wiki=False):return '<a class="skip" href="#main">跳至內容</a><header class="top"><a class="brand" href="slides.html">HUGGING FACE / 2026</a><nav>'+('<a href="slides.html">回到簡報</a>' if wiki else '<button class="toc-toggle">目錄</button>')+'<a href="wiki.html">Wiki 來源</a></nav></header>'
def htmlpage(title,body,script=''):return f'<!DOCTYPE html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><link rel="stylesheet" href="assets/style.css"></head><body>{body}{script}</body></html>'
sections=[]
for p in SL:
 if p['id']=='P01':body=p['body']
 else:body=(f'<p class="story-stage">{E(p["stage"])}</p>' if p.get('stage') else '')+f'<h2>{p["title"]}</h2><p class="takeaway">{p["takeaway"]}</p>'+(fig(p['diagram']) if p['diagram'] else p['body'])
 if p.get('reading'):body+=f'<p class="read-guide"><b>{"讀圖：" if p["diagram"] else "重點："}</b>{E(p["reading"])}</p>'
 if p['notes']:body+=f'<details><summary>技術補充</summary><p>{E(p["notes"])}</p></details>'
 body+=f'<footer class="source">{refs(p["wiki"])}'+('　｜　'+p['kind'] if p['diagram'] else '')+'</footer>'
 sections.append(f'<section class="slide" id="{p["id"]}" aria-label="{p["title"]}">{body}</section>')
groups=[]
for chapter in ['開始','事件概況','技術路徑','失效原因','防護重點','查閱來源']:
 ps=[p for p in SL if p['chapter']==chapter]
 groups.append(f'<div class="toc-group"><h3>{chapter}</h3>'+''.join(f'<a href="#{p["id"]}" data-go="{p["id"]}">{p["id"][1:]}　{p["title"]}</a>' for p in ps)+'</div>')
dialogs='<dialog id="toc" class="modal"><div class="dialog-head"><h2>簡報目錄</h2><button data-close="toc">關閉</button></div><div class="toc-grid">'+''.join(groups)+'</div></dialog><dialog id="zoom" class="modal zoom"><div class="dialog-head"><h2 id="zoom-title">架構圖</h2><button data-close="zoom">關閉</button></div><div class="zoom-area"><img id="zoom-image" class="diagram" alt=""></div></dialog>'
bottom='<nav class="bottom" aria-label="換頁"><div><button id="prev">上一頁</button> <button id="next" class="primary">下一頁</button></div><div class="position"><span class="chapter" id="chapter"></span><span id="counter" aria-live="polite"></span></div><button class="toc-toggle">目錄</button></nav>'
page=top()+'<main class="deck" id="main"><noscript><p class="nojs">停用 JavaScript 時，所有頁面會依序顯示。</p></noscript>'+''.join(sections)+'</main>'+bottom+dialogs
save(R/'slides.html',htmlpage('Hugging Face 事件｜圖解簡報',page,'<script src="assets/slides.js"></script>'))
save(R/'index.html',htmlpage('Hugging Face 事件｜圖解簡報',page,'<script src="assets/slides.js"></script>'))
DATA={p['id']:dict(title=p['title'],chapter=p['chapter']) for p in SL}
JS='''document.documentElement.classList.add('enhanced');
const meta=__META__, diagrams=__DIAGRAMS__, slides=[...document.querySelectorAll('.slide')];let current=0;
function show(id){let n=typeof id==='number'?id:slides.findIndex(s=>s.id===id);if(n<0)n=0;current=Math.min(slides.length-1,Math.max(0,n));slides.forEach((s,i)=>{s.classList.toggle('active',i===current);s.setAttribute('aria-hidden',String(i!==current))});const s=slides[current];document.getElementById('prev').disabled=current===0;document.getElementById('next').disabled=current===slides.length-1;document.getElementById('counter').textContent=`${current+1} / ${slides.length}`;document.getElementById('chapter').textContent=meta[s.id].chapter;document.querySelectorAll('#toc [data-go]').forEach(a=>a.setAttribute('aria-current',a.dataset.go===s.id?'page':'false'));history.replaceState(null,'','#'+s.id);window.scrollTo(0,0)}
document.getElementById('prev').onclick=()=>show(current-1);document.getElementById('next').onclick=()=>show(current+1);
document.querySelectorAll('.toc-toggle').forEach(b=>b.onclick=()=>document.getElementById('toc').showModal());
document.querySelectorAll('[data-close]').forEach(b=>b.onclick=()=>document.getElementById(b.dataset.close).close());
document.querySelectorAll('[data-go]').forEach(b=>b.onclick=e=>{e.preventDefault();const d=document.getElementById('toc');if(d.open)d.close();show(b.dataset.go)});
document.querySelectorAll('.enlarge').forEach(b=>b.onclick=()=>{const d=diagrams[b.dataset.diagram],im=document.getElementById('zoom-image');im.src=d.path;im.alt=d.desc;document.getElementById('zoom-title').textContent=d.label;document.getElementById('zoom').showModal()});
document.addEventListener('keydown',e=>{if(document.querySelector('dialog[open]')||/INPUT|BUTTON|SUMMARY|TEXTAREA/.test(e.target.tagName))return;if(e.key==='ArrowRight'){e.preventDefault();show(current+1)}if(e.key==='ArrowLeft'){e.preventDefault();show(current-1)}});
window.addEventListener('hashchange',()=>show(location.hash.slice(1)));show(location.hash.slice(1)||'P01');
'''.replace('__META__',json.dumps(DATA,ensure_ascii=False)).replace('__DIAGRAMS__',json.dumps(D,ensure_ascii=False))
JS=JS.replace('INPUT|BUTTON|SUMMARY|TEXTAREA','INPUT|SUMMARY|TEXTAREA')
save(AS/'slides.js',JS)
save(AS/'slide-map.json',json.dumps([{k:v for k,v in p.items() if k not in ['body','notes']} for p in SL],ensure_ascii=False,indent=2));save(AS/'wiki-data.json',json.dumps(W,ensure_ascii=False,indent=2))

entries=[]
for w in W:
 evid=''.join(f'<p><a href="#{e["source"]}">{e["source"]}</a> · <a href="sources/{e["source"]}.txt">文字快照</a> 第 {e["line"]} 行附近<br><code>{E(e["needle"])}</code></p>' for e in w['evidence'])
 entries.append(f'<article class="wiki-entry" id="{w["id"]}"><h2>{w["id"]}　{E(w["title"])}</h2><p class="definition">{E(w["summary"])}</p><details><summary>技術細節</summary><p>{E(w["technical"])}</p></details><p class="boundary">{E(w["boundary"])}</p><details><summary>來源與定位</summary><div class="evidence">{evid}</div></details><p class="related">相關概念：'+''.join(f'<a href="#{x}">{x}</a>' for x in w['related'])+'</p></article>')
source_titles={'S1':'OpenAI 初步說明','S2':'Hugging Face 技術調查','S3':'METR／Redwood 獨立調查','S4':'OpenAI 後續分析','S5':'Hugging Face 事件披露','S6':'Jinja 沙盒文件','S7':'h5py 資料集文件','S8':'Kubernetes 服務帳號','S9':'OWASP SSRF 防護'}
sources=''.join(f'<article class="source-record" id="{s["id"]}"><h3>{s["id"]}　<a href="{s["url"]}" target="_blank" rel="noopener">{source_titles[s["id"]]}</a></h3><p>{E(s["author"])} · {E(s["date"])}</p><details><summary>完整名稱與擷取紀錄</summary><p>{E(s["title"])}</p><p>{E(s["retrieved_at"])} · HTTP {s["status"]}<br>{E(s["scope"])}</p><p><a href="{s["snapshot"]}">來源快照</a>　<a href="sources/manifest.json">Manifest</a></p><code>{s["sha256"]}</code></details></article>' for s in S)
wiki=top(True)+'<main class="wiki-main" id="main"><h1>事件 Wiki</h1><p class="intro">先看一句話定義，需要時再展開細節與證據。</p><form class="search" id="search"><label class="skip" for="q">查詢 Wiki</label><input id="q" placeholder="輸入技術詞，例如 HDF5、Jinja、權限"><button type="submit">查詢</button></form><div id="results" class="results" aria-live="polite"></div><nav class="wiki-toc" aria-label="Wiki 目錄">'+''.join(f'<a href="#{w["id"]}">{w["id"]}　{w["title"]}</a>' for w in W)+'</nav>'+''.join(entries)+'<section id="sources" class="sources-list"><h2>9 篇原始來源</h2><p>事件報告與官方技術文件分開使用；一般原理不作為事件發生的證據。</p>'+sources+'</section></main>'
save(R/'wiki.html',htmlpage('事件 Wiki｜概念與證據',wiki,'<script src="assets/wiki.js"></script>'))
wikiJS='''const wiki=__DATA__;document.getElementById('search').onsubmit=e=>{e.preventDefault();const q=document.getElementById('q').value.trim().toLowerCase(),out=document.getElementById('results');out.replaceChildren();if(!q){out.textContent='請輸入技術詞。';return}const rank=wiki.map(w=>({w,score:w.tags.filter(t=>q.includes(t.toLowerCase())).reduce((s,t)=>s+t.length,0)+((w.title+w.summary).toLowerCase().includes(q)?q.length:0)})).filter(x=>x.score>0).sort((a,b)=>b.score-a.score||a.w.id.localeCompare(b.w.id));if(!rank.length){out.textContent='資料不足：沒有匹配的概念，請改寫或補充來源。';return}const p=document.createElement('p');p.textContent='候選概念如下，仍需確認來源是否足夠回答。';out.append(p);rank.slice(0,3).forEach(x=>{const a=document.createElement('a');a.href='#'+x.w.id;a.textContent=x.w.id+'　'+x.w.title;out.append(a)})};'''.replace('__DATA__',json.dumps(W,ensure_ascii=False))
wikiJS=wikiJS.replace('+((w.title+w.summary).toLowerCase().includes(q)?q.length:0)','+(w.title.toLowerCase().includes(q)?q.length*3:0)+(w.summary.toLowerCase().includes(q)?q.length:0)')
save(AS/'wiki.js',wikiJS)
# README.md is the single, independently maintained submission report.
print('Rebuilt',len(SL),'slides;',len(D),'formal diagrams;',len(W),'Wiki entries')

