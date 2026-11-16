# 플레이 링크와 검사 시험장 페이지를 index.html에서 다시 만든다
import base64
P='/tmp/claude-0/-home-user/875e994b-0182-5232-bcb1-555936fad427/scratchpad/play/'
s=open('/home/user/ghost-game/index.html').read(); body=s[s.index('<canvas'):s.index('</body>')]
u='assets/fonts/Galmuri11-Bold.woff2'; body=body.replace(u,'data:font/woff2;base64,'+base64.b64encode(open('/home/user/ghost-game/'+u,'rb').read()).decode())
g=open(P+'ghost-armor.html').read(); open(P+'ghost-armor.html','w').write(g[:g.index('<canvas')]+body)
t=open(P+'sword-test.html').read(); open(P+'sword-test.html','w').write(t[:t.index('<canvas')]+body+t[t.index('\n<div id="help">'):])
print('rebuilt')

# 저장소용 검사 시험장 (Vercel 등 정적 호스팅): 그림 경로를 ../assets/ 로
t=open(P+'sword-test.html').read().replace('"assets/', '"../assets/').replace("`assets/", "`../assets/")
open('/home/user/ghost-game/test/sword.html','w').write(t); print('test/sword.html')

# 골렘 시험장
t=open(P+'golem-test.html').read(); open(P+'golem-test.html','w').write(t[:t.index('<canvas')]+body+t[t.index('\n<div id="help">'):])
t=open(P+'golem-test.html').read().replace('"assets/', '"../assets/').replace("`assets/", "`../assets/")
open('/home/user/ghost-game/test/golem.html','w').write(t); print('test/golem.html')

# 투구 시험장 (투구 목록은 게임 코드에서 자동으로 읽는다)
t=open(P+'helm-test.html').read(); i=t.index('<canvas'); j=t.index('\n<div id="hpanel">'); open(P+'helm-test.html','w').write(t[:i]+body+t[j:])
t=open(P+'helm-test.html').read().replace('"assets/', '"../assets/').replace("`assets/", "`../assets/")
open('/home/user/ghost-game/test/helm.html','w').write(t); print('test/helm.html')
