# 米家目录型号缺口

以 APK 表的唯一 model 为分母，与发布集中所有非空 miio_model 精确匹配；不按品牌/status 过滤，不将缺口自动视为应补采商品。

|cate_name|已有型号|表内型号|覆盖率|缺口|
|---|---:|---:|---:|---:|
|个护与起居|16|1187|1.35%|1171|
|传感器|4|213|1.88%|209|
|其他|0|53|0.00%|53|
|出行车载|13|53|24.53%|40|
|办公学习|14|42|33.33%|28|
|卫浴|63|508|12.40%|445|
|厨房电器|289|1064|27.16%|775|
|安防|155|489|31.70%|334|
|宠物与植物|11|62|17.74%|51|
|影音娱乐|72|294|24.49%|222|
|插座开关|8|3138|0.25%|3130|
|清洁电器|192|725|26.48%|533|
|照明|19|2308|0.82%|2289|
|环境电器|280|1260|22.22%|980|
|路由网关|17|143|11.89%|126|
|运动健康|74|451|16.41%|377|

## 家电专项

按表内 model 的设备类型段精确归组；cate_name 为宽类，以下只是型号目录缺口，不代表参数覆盖率。空调包括 airc/aircondition（目录中也含控制器），扫地机沿用 vacuum 类型（目录中也含擦窗机）。电热水器仅取 waterheater 且官方 name 明含“电热水”的条目；不推断燃料种类。微波炉沿用 microwave 类型，不推断 oven 里的微蒸烤机；风扇不含 light 类型的风扇灯。完整缺口仍全部列于 cate_name 节。

### 空调：144/482，缺 338

|model|name|pd_id|
|---|---|---:|
|090615.airc.a07s|平头熊空调小精灵(Mesh2.0)|26068|
|090615.airc.fsair|平头熊F系列空调三合一旋钮面板(Mesh2.0)|28440|
|090615.airc.hyshn1|皓逸Smart Home空调旋钮面板|26280|
|090615.airc.k20|OF VRF空调内机|24504|
|090615.airc.x1air|平头熊空调三合一旋钮面板|23741|
|090615.aircondition.ktf|智能空调(VRF)|75704|
|090615.aircondition.ktp|VRF空调内机|16410|
|090615.aircondition.lkt|中央空调线控网关(MESH)|13532|
|090615.aircondition.lnk|中央空调线控网关 (PTXZN)|4359|
|090615.aircondition.x6c|X6 空调面板(PTX)|13445|
|759413.aircondition.iez|日立中央空调|70688|
|aden.airc.12k|VINO 轻音 变频空调 (1.5匹 一级能效)|22442|
|aden.airc.a6|VINO变频空调3匹(新二级能效)|2953|
|aden.airc.vn1p5|VINO 变频空调 (1.5匹 三级能效)|27599|
|aden.aircondition.a1|VINO变频空调（三级能效）|741|
|aden.aircondition.a2|VINO变频空调（一级能效）|842|
|aden.aircondition.a4|VINO变频空调2匹2级能效|1528|
|aden.aircondition.a7|VINO变频空调2匹(新二级能效)|3793|
|aden.aircondition.ad2p1|变频风管机|13677|
|aden.aircondition.vf1p5|VINO变频空调1.5匹（一级能效）|15588|
|aden.aircondition.xfkt1|VINO新风变频空调（一级能效）|10086|
|aizyy.airc.air01|众益洋中央空调控制器mesh2.0 UItra版|28926|
|aupu.aircondition.kc26a|奥普厨房空调KC-26/A|14135|
|aux.aircondition.hc1|奥克斯智能空调|72|
|aux.aircondition.v1|奥克斯智能空调|49|
|baiten.airc.air01|贝兴中央空调控制器(MESH2.0)|23603|
|baiten.airc.air02|贝兴VRF空调|26093|
|baiten.airc.dw|贝兴通用智能空调控制器(MESH2.0)|33168|
|bean.aircondition.tc01|智能空调助手RCS-Mesh版|16549|
|btzn.aircondition.v1|比特空调控制器|68848|
|bwk.airc.air01|泊林之风智能空调-BL1|25386|
|bymiot.airc.wlv2|未来居无线空调线控器|80636|
|bymiot.aircondition.ir2|未来居空调控制器（红外版）|70363|
|bymiot.aircondition.v1|未来居中央空调控制器|67329|
|bymiot.aircondition.wl2|未来居无线中央空调控制器|71767|
|chuangmi.aircondition.a|空调|75256|
|chzyj.airc.guiji|长虹空调|83630|
|chzyj.airc.test|长虹空调|82970|
|chzyj.airc.xdl|长虹中央空调|83853|
|daikin.airc.k32|大容量厨房(标准版/黑奢版)|79984|
|daikin.aircondition.k1|智能3D气流风管式温湿平衡型/3D气流风管式温湿平衡型|77745|
|daikin.aircondition.k10|单向气流嵌入式|77761|
|daikin.aircondition.k11|智能感知环绕气流嵌入式|77762|
|daikin.aircondition.k12|环绕气流嵌入式(全效型/低矮型)|77763|
|daikin.aircondition.k13|中静压风管机(全效型/低矮型)|77764|
|daikin.aircondition.k14|自由静压风管式|77765|
|daikin.aircondition.k15|内藏落地式(全效型/低矮型)|77766|
|daikin.aircondition.k16|明装落地式(全效型/低矮型)|77767|
|daikin.aircondition.k17|挂壁式|77768|
|daikin.aircondition.k18|智能3D气流风管式 新风净化型/3D气流风管式 新风净化型|77749|
|daikin.aircondition.k19|超薄风管式新风净化型|77750|
|daikin.aircondition.k2|超薄风管式温湿平衡型|77747|
|daikin.aircondition.k20|灯槽专用室内机标准型|77758|
|daikin.aircondition.k21|灯槽专用室内机Air Mirror黑奢型|77760|
|daikin.aircondition.k3|衣帽间防潮嵌入式标准式|77748|
|daikin.aircondition.k4|智能3D气流风管式PM2.5净化型/3D气流风管式PM2.5净化型|77751|
|daikin.aircondition.k5|超薄风管式PM2.5净化型/超薄风管式标准型|77752|
|daikin.aircondition.k6|智能3D气流风管式标准型/3D气流风管式标准型|77753|
|daikin.aircondition.k7|超薄风管式大容量型|77754|
|daikin.aircondition.k8|卫浴用嵌入式标准型|77755|
|daikin.aircondition.k9|高耐久厨房用嵌入式标准型/大容量型|77756|
|demry.airc.temp|DigSmart中央空调控制器|30143|
|demry.airc.tempp|DigSmart中央空调线控器|31162|
|dhdzkj.airc.air01|迪航空调智能控制网关 G/Z 770|17931|
|dnake.airc.temp|狄耐克VRF中央空调控制器(Mesh2.0)|34502|
|dnk.airc.dag60a|狄耐克四季生态空调|22867|
|dpurat.airc.dbdf|德普莱太环控一体机新风除湿空调|25584|
|fawad.airc.5001|FOWAD空调VRF网关Mesh2.0|34380|
|fawad.aircondition.3010|FOWAD 空调温控器2|14652|
|fawad.aircondition.3019|FOWAD空调控制器尊享版|13572|
|idelan.aircondition.g1|金兴智能空调|244|
|idelan.aircondition.g2|金兴智能空调|243|
|idelan.aircondition.v1|金兴智能空调|101|
|idelan.aircondition.v2|金兴智能空调|185|
|iracc.aircondition.d19|好享+智能空调网关|66113|
|juhl.airc.room|海信智能室温线控器|80521|
|juhl.airc.water|海信智能水温线控器|80522|
|juhl.aircondition.a11|智能空调|66503|
|juhl.aircondition.hvac|海信智能中央空调|79502|
|klwdz1.airc.001|VRF智能空调|25333|
|klwdz1.airc.003|VRF智能空调MESH版|27899|
|lemesh.airc.air01|情景Mesh空调室内机控制器|19340|
|lemesh.airc.air02|中弘VRF中央空调控制器(MESH2.0版)|26668|
|lemesh.airc.air03|中弘VRF中央空调控制器PRO(MESH2.0版)|27683|
|lemesh.airc.b19d|中弘两联供空调控制器(MESH2.0版)|28491|
|lemesh.airc.b27m|中弘空调室内机控制器(MESH2.0版)|27838|
|lemesh.aircondition.a01|HT智能空调控制器（Mesh版）|15797|
|line.airc.air02|邮科通信空调伴侣K6|22947|
|line.airc.fktbl|方舟鱼空调伴侣K6|27737|
|line.airc.ktbl|LineHope空调伴侣K6|27661|
|linp.aircondition.vrf02|领普VRF空调|15500|
|lonink.airc.ln051|朗宁风管机空调控制器WiFi|28788|
|lonink.airc.ln052m|朗宁风管机空调控制器Mesh2.0|28361|
|lonink.airc.ln059|朗宁VRF中央空调控制器Pro Mesh2.0|26849|
|lonink.airc.ln059a|朗宁VRF中央空调控制器ProAI Mesh2.0|37683|
|lonink.airc.ln059e|朗宁VRF中央空调控制器ProE Mesh2.0|29641|
|lumi.aircondition.acn05|Aqara空调伴侣 P3|69068|
|maxi.airc.a07s|迈斯空调小精灵Mesh2.0|26398|
|maxi.airc.air03|迈斯小精灵空调控制器|19342|
|maxi.airc.air04|迈斯VRF中央空调控制器|20483|
|maxi.airc.air08|迈斯VRF空调控制器Mesh2.0|27521|
|maxi.airc.airm1|品达小精灵空调控制器Mesh2.0|35667|
|maxi.airc.airw1|品达小精灵空调控制器WIFI版|35565|
|maxi.airc.ln069s|品达中央空调|25051|
|maxi.aircondition.air02|迈斯风管机控制器A06B|15840|
|maxi.aircondition.m07|中央空调|76504|
|mbo.airc.mac35|meipont变频空调|17758|
|mbo.aircondition.mah35|meipont热泵空调|16804|
|mhaq.aircondition.miair|三菱重工海尔·智能空调|71403|
|midea.aircondition.v1|美的空调-i青春|45|
|midea.aircondition.xa1|美的空调 - 酷金|129|
|midea.aircondition.xa2|美的空调 - 酷金|360|
|miir.aircondition.ir01|空调遥控|65724|
|miir.aircondition.ir02|空调遥控|65723|
|miot.aircondition.cl801|cl801|74698|
|miot.aircondition.v1|智能空调|9827|
|mirsz.airc.ac300s|罗威亚中央空调|28752|
|mirsz.airc.air9|罗威亚中央空调智能温控器|33437|
|nwt.airc.ac0105|NWT 变频空调|21670|
|nwt.airc.max|NWT智能移动空调MAX|36938|
|nwt.airc.wap31a|NWT互联网移动空调Pro|18423|
|nwt.aircondition.26eaw1|NWT互联网移动空调|2389|
|nwt.aircondition.26ebw1|NWT智能移动空调|15195|
|ptx.airc.f1kt1|平头熊三合一屏显空调面板（F1)|37123|
|ptx.airc.fgkt1|平头熊三合一屏显空调面板(梵高）|34430|
|qdhkl.airc.19se|中弘VRF中央空调控制器MESH2.0|28690|
|qdhkl.airc.a19s|中弘VRF空调Ultra|28418|
|qdhkl.airc.a42|中弘两联供空调室内机|27675|
|qdhkl.airc.acp|中弘VRF空调|82092|
|qdhkl.airc.b19c|中弘VRF中央空调控制器PRO MESH2.0|32164|
|qdhkl.airc.b19cd|中弘两联供空调控制器PRO MESH2.0|31367|
|qdhkl.airc.b19cm|中弘VRF中央空调控制器(MESH2.0版)|35421|
|qdhkl.airc.b19m|中弘VRF中央空调控制器(MESH版)|18764|
|qdhkl.airc.b19sep|中弘VRF中央空调控制器SE PRO MESH2.0|39889|
|qdhkl.airc.b25p|中弘空调室内机控制器Ultra(Wi-Fi版)|29377|
|qdhkl.airc.b27m|中弘空调室内机控制器(MESH2.0版)|35433|
|qdhkl.airc.b27p|中弘空调室内机控制器PRO(Wi-Fi版)|36541|
|qdhkl.airc.b27se|中弘空调室内机控制器SE MESH2.0|29869|
|qdhkl.airc.ln0589|LONINK VRF空调控制器PRO（Mesh）|21543|
|qdhkl.airc.s26se|中弘智能空调旋钮温控器MESH2.0|35429|
|qdhkl.aircondition.ac|VRF空调|8494|
|qdhkl.aircondition.b23|中弘空调室内机控制器(WIFI)|8491|
|qdhkl.aircondition.b25|中弘空调室内机控制器(MESH)|9507|
|qdhkl.aircondition.b27|中弘空调室内机控制器(Wi-Fi版)|15824|
|qdhkl.aircondition.loac|朗宁VRF空调室内机|13447|
|qdhkl.aircondition.md01|苏米中央空调控制器|4229|
|saec.airc.rac|三菱电机空调|80096|
|scdvb.airc.ktmini|SoChuang空调控制器Mini|37089|
|scdvb.airc.llg20|SoChuang 两联供空调智能控制器|38591|
|scdvb.airc.t001|SoChuang VRF中央空调控制器 Ultra|24993|
|scdvb.aircondition.acm|蓝牙VRF中央空调控制器|14050|
|shadow.airc.air01|迅透智能户外空调|24586|
|slf.aircondition.air03|智拉斐全屏空调控制器（D8）|8961|
|slf.aircondition.air04|智拉斐旋钮空调温控器（HR7）|9332|
|symi.airc.air01|亖米空调地暖新风控制器|31466|
|symi.airc.smvrf|亖米VRF中央空调控制器MESH2.0|33499|
|szmq.airc.znkt02|麦克维尔智能空调|80632|
|tofan.airc.air|YOOMI空调控制器MESH2.0|27400|
|tofan.airc.air01m|悠觅空调地暖新风控制器|34098|
|tofan.airc.air02|悠觅VRF空调控制器MESH2.0|29729|
|tofan.airc.dlair|悠觅空调地暖控制器|34330|
|viomi.airc.m1|meekee 1P|2981|
|viomi.airc.m2|meekee 1.5P|2982|
|viomi.airc.m3|meekee 2P|2983|
|viomi.airc.m4|meekee 3P|2984|
|viomi.airc.sd26|云米AI空调 Smart 2S 1.5P (新一级)|17565|
|viomi.airc.sd28|云米AI空调 Super 3柜机3P (新一级)|17568|
|viomi.airc.sd34|云米AI空调Super 3 Max 1.5P（超一级）|24229|
|viomi.airc.sd35|云米AI空调Super 2 1.5P（超一级）|24230|
|viomi.airc.sd36|云米AI空调Smart 3 Max 2P（新一级）|24232|
|viomi.airc.sd37|云米AI空调 Smart 3 1.5P 新1级|24253|
|viomi.airc.y119|Smart AC A2 Pro-18K|18269|
|viomi.aircondition.sd01|Space E 1.5P(新版)|10724|
|viomi.aircondition.sd02|Space X 1.5P(新版)|10725|
|viomi.aircondition.sd03|Smart 2S 新版|10695|
|viomi.aircondition.sd06|Super 2S (除菌版) 1P|10736|
|viomi.aircondition.sd07|Super 2S (除菌版) 1.5P|10737|
|viomi.aircondition.sd08|Smart 2S (除菌版) 2P|10727|
|viomi.aircondition.sd09|Smart 2S (除菌版) 3P|10728|
|viomi.aircondition.sd10|Super 2 (柜式柔风版) 2P|10699|
|viomi.aircondition.sd11|Super 2 (柜式柔风版) 3P|10700|
|viomi.aircondition.sd12|Smart 2 Max 新版|10722|
|viomi.aircondition.sd15|Super 2 (语音版) 1P|10877|
|viomi.aircondition.sd16|Super 2 (语音版) 1.5P|10878|
|viomi.aircondition.sd17|Super 2 Pro（除菌版）1.5P|11015|
|viomi.aircondition.sd18|Smart 2（除菌版）2P|11013|
|viomi.aircondition.sd19|Smart 2（除菌版）3P|11014|
|viomi.aircondition.sd22|Super 3 1.5P|16616|
|viomi.aircondition.sd23|Super 3 2P|16618|
|viomi.aircondition.sd24|云米AI空调 Super 3 Pro 1.5P（新一级）|16619|
|viomi.aircondition.v10|Royal Pro(AI语音人感版)|1587|
|viomi.aircondition.v21|Crown-22A|1736|
|viomi.aircondition.v22|Crown-28A|1735|
|viomi.aircondition.v23|Crown-36A|1734|
|viomi.aircondition.v24|Crown-56A|1733|
|viomi.aircondition.v25|Crown-71A|1731|
|viomi.aircondition.v26|King Pro(AI空净版)|1732|
|viomi.aircondition.v28|Royal(AI语音版) 2P|2310|
|viomi.aircondition.v29| Royal(AI语音版) 3P|2312|
|viomi.aircondition.v30|King Pro-A （AI空净版）|2313|
|viomi.aircondition.v31|King 1S(AI柔风版) 1.5P|2314|
|viomi.aircondition.v32|King  1X 1P|2301|
|viomi.aircondition.v33|King  1X 1.5P|2302|
|viomi.aircondition.v34| King 1A 1P|2315|
|viomi.aircondition.v35| King 1A 1.5P|2316|
|viomi.aircondition.v37|Crown-72A3|5976|
|viomi.aircondition.v38|Crown-26A3|6605|
|viomi.aircondition.v39|Crown-35A3|6606|
|viomi.aircondition.v40|Crown-50A3|6607|
|viomi.aircondition.v6|King(1P)|1590|
|viomi.aircondition.v7|King|1589|
|viomi.aircondition.v8|King 1S(AI柔风版)|1565|
|viomi.aircondition.v9|Royal（AI语音版）|1588|
|viomi.aircondition.y1|Milano（柜式 柔风版）2P|2317|
|viomi.aircondition.y10|Milano 1.5P|2319|
|viomi.aircondition.y101|Milano 2S 1.5P|7195|
|viomi.aircondition.y103|Milano 2T 1.5P|7235|
|viomi.aircondition.y11|iCool 1C 1P|2320|
|viomi.aircondition.y12|iCool 1C 1.5P|2321|
|viomi.aircondition.y13|iCool 1P|2322|
|viomi.aircondition.y14|iCool 1.5P|2323|
|viomi.aircondition.y15|iCool 1S 1.5P|2438|
|viomi.aircondition.y2|Milano（柜式 柔风版）3P|2318|
|viomi.aircondition.y25|iCool 1V 1.5P|3094|
|viomi.aircondition.y26|iCool 1N 1.5P|3095|
|viomi.aircondition.y27|Milano 1N 1P|3130|
|viomi.aircondition.y28|Milano 1N 1.5P|3131|
|viomi.aircondition.y29|iCool 1S 1P(新能效)|3219|
|viomi.aircondition.y3|Milano（柜式）2P|2324|
|viomi.aircondition.y30|iCool 1S 1.5P(新能效)|3220|
|viomi.aircondition.y31|iCool 1P(新能效)|3227|
|viomi.aircondition.y32|iCool 1.5P(新能效)|3228|
|viomi.aircondition.y33|iCool 1H 1P|3319|
|viomi.aircondition.y34|iCool 1H 1.5P|3320|
|viomi.aircondition.y35|iCool 1R 1P|3321|
|viomi.aircondition.y36|iCool 1R 1.5P|3322|
|viomi.aircondition.y37|Milano 1C 2P(新能效)|3323|
|viomi.aircondition.y38|Milano 1C 3P(新能效)|3324|
|viomi.aircondition.y4|Milano（柜式）3P|2325|
|viomi.aircondition.y43|Smart 1S 1P|3346|
|viomi.aircondition.y44|Smart 1S 1.5P|3347|
|viomi.aircondition.y45|Smart 1C 1P|3348|
|viomi.aircondition.y46|Smart 1C 1.5P|3349|
|viomi.aircondition.y47|Smart 1X 1P|3350|
|viomi.aircondition.y48|Smart 1X 1.5P|3351|
|viomi.aircondition.y49|Smart 1P|3352|
|viomi.aircondition.y5|Milano 1S（柔风版）1P|2300|
|viomi.aircondition.y50|Smart 1.5P|3353|
|viomi.aircondition.y51|iCool 2P|3354|
|viomi.aircondition.y52|iCool 3P|3355|
|viomi.aircondition.y53|Navi（柜式 柔风版）2P|3374|
|viomi.aircondition.y54|Navi（柜式 柔风版）3P|3375|
|viomi.aircondition.y55|Navi 1P|3432|
|viomi.aircondition.y56|Navi 1.5P|3433|
|viomi.aircondition.y57|Smart 2P|3434|
|viomi.aircondition.y58|Smart 3P|3435|
|viomi.aircondition.y59|Smart 1X 2P|3436|
|viomi.aircondition.y6|Milano 1S（柔风版）1.5P|2303|
|viomi.aircondition.y60|Smart 1X 3P|3438|
|viomi.aircondition.y64|Navi 2 1P|4502|
|viomi.aircondition.y65|Navi 2 1.5P|4503|
|viomi.aircondition.y66|iCool 2 Max 2P|4538|
|viomi.aircondition.y67|Milano 2 1P|4631|
|viomi.aircondition.y68|Milano 2 1.5P|4632|
|viomi.aircondition.y69|Space X 1.5P|4633|
|viomi.aircondition.y7|Milano（柔风版）1P|2326|
|viomi.aircondition.y71|Space E 1.5P|4768|
|viomi.aircondition.y72|Smart 2 1P|4823|
|viomi.aircondition.y73|Smart 2 1.5P|4824|
|viomi.aircondition.y74|Smart 2 Max 2P|4904|
|viomi.aircondition.y75|Smart 2A|4967|
|viomi.aircondition.y76|Smart 2A|4971|
|viomi.aircondition.y78|Smart 2C 1.5P|4988|
|viomi.aircondition.y79|Milano 2 Pro 1P|5035|
|viomi.aircondition.y8|Milano（柔风版）1.5P|2327|
|viomi.aircondition.y80|Milano 2 Pro 1.5P|5036|
|viomi.aircondition.y81|Smart 2C 1P|5174|
|viomi.aircondition.y82|Smart 2C 1.5P|5175|
|viomi.aircondition.y83|Navi 2 2P|5176|
|viomi.aircondition.y84|Navi 2 3P|5177|
|viomi.aircondition.y85|Navi 2C 2P|5178|
|viomi.aircondition.y86|Navi 2C 3P|5179|
|viomi.aircondition.y88|Smart AC A1-12K|5931|
|viomi.aircondition.y89|Smart AC A1-18K|5932|
|viomi.aircondition.y9|Milano 1P|2328|
|viomi.aircondition.y99|Smart 2S 1.5P|7161|
|xhuan.airc.acnew|苏米VRF空调室内机|30268|
|xhuan.airc.air|苏米中央空调控制器Mesh2.0|26368|
|xhuan.airc.b27se|苏米中央空调控制器Pro Mesh2.0|33046|
|xhuan.aircondition.ac01|苏米VRF控制器|6893|
|xiaomi.airc.2r09r1|强劲风 风管机 超4匹 超一级能效|34367|
|xiaomi.airc.2r19r1|人感风 双出风 风管机 大4匹 超一级能效|34368|
|xiaomi.airc.3rf1r1|中央空调Pro（适用于米家中央空调）|35098|
|xiaomi.airc.3rf2r2|中央空调Pro 双风轮（适用于中央空调 双风轮）|34970|
|xiaomi.airc.3ysjkk|小米智能空气管理面板Lite 演示|40662|
|xiaomi.airc.ar02kk|风管机Pro 1.5匹 超一级能效|22728|
|xiaomi.airc.ar08r1|强劲风 风管机 超3匹 超一级能效|29888|
|xiaomi.airc.arf1r1|中央空调Pro（适用于米家中央空调）|21479|
|xiaomi.airc.arf2r1|中央空调Pro（适用于米家中央空调）|29930|
|xiaomi.airc.axxxxx|小米智能空气管理面板|22688|
|xiaomi.airc.ayyyyy|小米智能空气管理面板|24786|
|xiaomi.airc.f55ysj|空调 巨省电Pro 柔风版 大1.5匹 超一级能效|34984|
|xiaomi.airc.frlh00|空调 巨省电Pro 柔风版 立式大3匹 超一级能效|34977|
|xiaomi.airc.h09h00|小米空调巨省电 1.5匹 一级 适用米家速冷静|16496|
|xiaomi.airc.h10h00|小米空调巨省电 1匹 一级 适用米家速冷静|20810|
|xiaomi.airc.h10r00|小米空调巨省电 1匹 一级 适用米家速冷静|20811|
|xiaomi.airc.h21h00|空调 上出风Pro 1.5匹 超一级能效|20805|
|xiaomi.airc.h40h00|空调Pro 健康风 1.5匹超一级能效|24477|
|xiaomi.airc.h46h00|空调Pro 人感上出风 1.5匹 超一级能效|25022|
|xiaomi.airc.h65h00|空调 强劲风 至尊版 超1.5匹 超一级能效|35730|
|xiaomi.airc.r09h00|小米空调巨省电 1.5匹 一级 适用米家速冷静|16498|
|xiaomi.airc.r10h00|小米空调巨省电 1匹 一级 适用米家速冷静|20812|
|xiaomi.airc.r24r00|空调 巨省电Pro  1.5匹 超一级能效|19298|
|xiaomi.airc.rr0r00|空调 新风Pro 双出风 立式3匹 超一级能效|18010|
|xiaomi.airc.rr7r00|空调 新风Pro 双出风 立式3匹 超一级能效（冰晶白）|22472|
|xiaomi.airc.rrar00|空调 巨省电Pro 立式3匹 超一级能效|22654|
|xiaomi.airc.rrhr00|新风空调Pro 人感双出风 立式3匹 超一级能效|25711|
|xiaomi.airc.rrrysj|空调 强劲风Pro 至尊版 立式超3匹 超一级能效|35822|
|xiaomi.aircondition.c14|小米巨省电立式空调（3匹/变频/新三级能效）|4117|
|xiaomi.aircondition.c25|米家空调 自然风 立式 3 匹（新一级能效）|8575|
|xiaomi.aircondition.c30|空调 柔风 立式3匹新一级（含速冷静）|11300|
|xiaomi.aircondition.c32|小米巨省电立式空调 （3匹/变频/新一级能效）|11590|
|xiaomi.aircondition.c35|米家新风空调立式（3匹 新一级能效）|13259|
|xiaomi.aircondition.c38|小米巨省电立式空调 （2匹/变频/新一级能效）|13600|
|xiaomi.aircondition.m3|米家空调 自然风 1.5匹 （新一级能效）|8287|
|xiaomi.aircondition.mc9|小米巨省电立式空调（2匹/变频/新三级能效）|3306|
|xiaomi.aircondition.mt0|米家新风空调 （尊享版 1.5匹）|8374|
|xiaomi.aircondition.mt8|小米巨省电空调 （1.5匹/变频/新一级能效）|3682|
|xl2024.airc.air|Pluslife VRF中央空调控制器|28864|
|yeelink.airc.vrf1|Yeelight VRF空调控制器|17971|
|yj1226.airc.air|今闪空调控制器Mesh2.0|25984|
|yj1226.airc.air01|今闪中央空调内机|28135|
|yj1226.airc.air02|今闪空调室内机控制器|29611|
|zhimi.aircondition.ma3|米家互联网空调（三级能效）|978|
|zhimi.aircondition.v1|智米全直流变频空调|195|
|zxkj.aircondition.kt22|正熙户外便携空调|9871|
|zyzy1.aircondition.0715|空调|73650|
|zyzy1.aircondition.y712|智能空调|6263|

### 扫地机：90/165，缺 75

|model|name|pd_id|
|---|---|---:|
|dji.vacuum.romo|DJI ROMO|80925|
|dreame.vacuum.ma1808|米家扫拖机器人1C|72473|
|dreame.vacuum.mc1808|米家扫拖机器人1C|66181|
|dreame.vacuum.p2028|追觅Z10 Pro|72190|
|dreame.vacuum.p2140|米家扫拖机器人2C|71742|
|eco.vacuum.dibao|科沃斯扫地机器人|84726|
|eco.vacuum.tveglj|DEEBOT N50|82350|
|gdyimu.vacuum.g1m|Lydsto惯导扫拖机器人G1M|5961|
|gdyimu.vacuum.r1|Lydsto扫拖一体机R1A|72192|
|gdyimu.vacuum.r1da|Lydsto智能扫拖机器人R1DA|73349|
|hanyi.vacuum.m7pro|美倾互联网智能扫地机器人|71708|
|hanyi.vacuum.m8pro|美倾M8互联网智能扫地机器人|74720|
|iot.vacuum.cc1|ZN-智能擦窗机器人|20827|
|jdyw.vacuum.t300|友望扫地机器人T300|81745|
|jdyw.vacuum.u300p|友望扫地机器人U300|80719|
|jdyw.vacuum.u400|友望扫地机器人U400|82918|
|jdyw.vacuum.u400m|友望扫地机器人U400 Max|84732|
|mijia.vacuum.b108zb|米家扫拖机器人3S|13068|
|narwa.vacuum.001|云鲸逍遥系列 001|81646|
|narwa.vacuum.ax11|云鲸逍遥系列 002（超薄全能基站版）|82028|
|narwa.vacuum.ax12|云鲸逍遥系列 002|82029|
|narwa.vacuum.ax17|云鲸智能扫拖一体机器人 J5 pure|82041|
|narwa.vacuum.ax17p|云鲸智能扫拖一体机器人 J5经典款|84271|
|narwa.vacuum.ax18|云鲸智能扫拖一体机器人 J5Max|82036|
|narwa.vacuum.ax19|云鲸智能扫拖一体机器人 J5Max(超薄基站版)|82037|
|narwa.vacuum.ax24|云鲸活水履带洗地机器人 J6|82810|
|narwa.vacuum.ax25|云鲸活水履带洗地机器人 J6（超薄基站）|82811|
|narwa.vacuum.cx2|云鲸逍遥系列 002 Max|82018|
|narwa.vacuum.cx3mi|云鲸逍遥系列 001（轻集尘版）|81647|
|narwa.vacuum.cx3p|云鲸逍遥全智能清洁机器人 001 Pure|81367|
|narwa.vacuum.cx4|云鲸逍遥全智能清洁机器人 001 Max|81316|
|narwa.vacuum.cx7|云鲸逍遥系列 002 Max（超薄基站版）|82027|
|narwa.vacuum.j4lmi|云鲸智能扫拖一体机器人 J4Lite|81648|
|narwa.vacuum.j4mi|云鲸 J4|80780|
|narwa.vacuum.j4pmi|云鲸智能拖扫一体机器人 J4增强版|81330|
|narwa.vacuum.j5|云鲸 J5|81644|
|narwa.vacuum.j5c|云鲸智能扫拖一体机器人 J5C|82808|
|narwa.vacuum.j5x|云鲸 J5X|81645|
|narwa.vacuum.j64|云鲸活水履带洗地机器人 JX|83818|
|narwa.vacuum.j64p|云鲸 活水履带洗地机器人 JX Pro|84766|
|narwa.vacuum.j65|云鲸活水履带洗地机器人 JX（超薄基站）|83819|
|narwa.vacuum.j72|云鲸 活水履带洗地机器人 JX Ultra|84620|
|narwa.vacuum.j78|云鲸 活水履带洗地机器人 JX Ultra Plus|84621|
|narwa.vacuum.r37|云鲸 活水履带洗地机器人 J6经典版|84683|
|narwa.vacuum.x30|云鲸AI活水履带洗地机器人 逍遥003|83820|
|narwa.vacuum.x31|云鲸AI活水履带洗地机器人 逍遥003（超薄基站版）|83821|
|narwa.vacuum.x38|云鲸 AI活水履带洗地机器人 逍遥003 Ultra|84682|
|onej.vacuum.clean|信社真湿擦智能擦窗机YW703|16857|
|roborock.vacuum.a01|石头扫地机器人 E4|67932|
|roidmi.vacuum.r1b|睿米扫拖机器人EVE|73690|
|roidmi.vacuum.sdj60|ROIDMI EVE MAX|11223|
|roidmi.vacuum.v1|ROIDMI手持无线吸尘器|584|
|roidmi.vacuum.v60|睿米扫拖机器人EVE|69844|
|roidmi.vacuum.v62|ROIDMI EVE CC|78053|
|roidmi.vacuum.v66|睿米真全能扫拖机器人|72592|
|viomi.vacuum.v11|云米互联网扫拖机器人 视觉导航版|67980|
|viomi.vacuum.v12|云米互联网扫拖机器人X2（激光导航版）|68005|
|viomi.vacuum.v13|Viomi V3|68241|
|viomi.vacuum.v15|云米AI扫拖机器人Alpha 2 Pro|69398|
|viomi.vacuum.v17|云米互联网集尘扫拖机器人|69619|
|viomi.vacuum.v20|云米集尘扫拖机器人凌厉-UV|71566|
|viomi.vacuum.v21|云米集尘扫拖机器人ALPHA-UV|71605|
|viomi.vacuum.v24|云米5GIOT扫拖机器人凌厉 2|72141|
|viomi.vacuum.v25|云米互联网扫拖机器人X3|72142|
|viomi.vacuum.v27|云米AI扫拖机器人 Alpha 2 Plus|72349|
|viomi.vacuum.v29|云米互联网扫拖机器人Eagle|72397|
|viomi.vacuum.v3|云米互联网扫地机 Pro|66085|
|viomi.vacuum.v37|云米AI集尘扫拖机器人Alpha Lite|73648|
|viomi.vacuum.v45|云米AI洗烘除菌扫拖机器人Alpha 3|74907|
|viomi.vacuum.v49|云米AI全能扫拖机器人Alpha 3 Pro|76176|
|viomi.vacuum.v6|云米扫地机器人PRO|66708|
|xiaomi.vacuum.ov21cn|米家扫拖机器人 5 Pro|21540|
|xiaomi.vacuum.ov31cn|米家扫拖机器人 M40 S|23191|
|xiaomi.vacuum.ov42cn|米家扫拖机器人 5C|24754|
|zhimi.vacuum.xa3|Lydsto扫拖一体机S1|73200|

### 冰箱：69/279，缺 210

|model|name|pd_id|
|---|---|---:|
|bshcn.fridge.1ade0c|博世奢嵌10系下嵌式冰箱|84225|
|bshcn.fridge.1hd30c|博世进口嵌入式冰箱|83376|
|bshcn.fridge.2053vc|西门子灵动储鲜多门冰箱|83293|
|bshcn.fridge.21ade0|博世奢嵌10系下嵌式冰箱|84226|
|bshcn.fridge.2aa50c|博世M8s法式多门冰箱|83149|
|bshcn.fridge.2aa99c|博世零嵌活氧净8系多门冰箱|84389|
|bshcn.fridge.2ea20c|博世零嵌6系多门冰箱|84221|
|bshcn.fridge.2ea97c|博世零嵌活氧净6系多门冰箱|84222|
|bshcn.fridge.2va20c|博世零嵌活氧净6系多门冰箱|84217|
|bshcn.fridge.2va97c|博世零嵌活氧净8系多门冰箱|84219|
|bshcn.fridge.6hfd0c|博世奢嵌10系两门冰箱|84387|
|bshcn.fridge.72aa34|西门子恒鲜零度多门冰箱|83381|
|bshcn.fridge.88hva5|西门子零嵌超氧L5多门冰箱|83881|
|bshcn.fridge.8aa26c|博世小平安Z830活氧净十字门冰箱|83868|
|bshcn.fridge.8aa28c|博世零嵌活氧净8系多门冰箱|83880|
|bshcn.fridge.8aa63c|博世维他鲜动力法式多门冰箱|83288|
|bshcn.fridge.8aa99c|博世零嵌活氧净8系多门冰箱|83879|
|bshcn.fridge.8eaa57|西门子零嵌超氧L7多门冰箱|83886|
|bshcn.fridge.8eaa63|西门子零嵌超氧L7多门冰箱|83884|
|bshcn.fridge.8va26c|博世小平安Z620活氧净Lite十字门冰箱|83870|
|bshcn.fridge.8va59c|博世活氧净对开门冰箱|83286|
|bshcn.fridge.92aa25|西门子超氧零度仓3门对开|83377|
|bshcn.fridge.9aa21c|博世全嵌活氧净8系多门冰箱|84520|
|bshcn.fridge.9aa26c|博世全嵌活氧净6系多门冰箱|84517|
|bshcn.fridge.9aa28c|博世全嵌活氧净8系多门冰箱|84519|
|bshcn.fridge.9aa31c|博世全嵌活氧净8系多门冰箱|84518|
|bshcn.fridge.9aw27c|博世全嵌活氧净8系多门冰箱|84524|
|bshcn.fridge.9bv163|西门子平嵌P3十字门冰箱|84105|
|bshcn.fridge.9va26c|博世小平安P625活氧净Plus十字门冰箱|83875|
|bshcn.fridge.aa256c|西门子法式多门零嵌冰箱|82159|
|bshcn.fridge.aa349c|西门子无界Pro超氧真空舱多门冰箱|83122|
|bshcn.fridge.aa657c|西门子无界Pro超氧真空舱多门冰箱|83120|
|bshcn.fridge.bv120c|西门子冰立方平嵌315自动制冰十字门冰箱|84104|
|bshcn.fridge.bv156c|西门子平嵌P3十字门冰箱|84106|
|bshcn.fridge.bv163c|西门子冰立方平嵌315自动制冰十字门冰箱|84103|
|bshcn.fridge.bva56c|西门子冰立方P520超氧Plus十字门冰箱|83873|
|bshcn.fridge.bva58c|西门子冰立方P520超氧Plus十字门冰箱|83871|
|bshcn.fridge.bva61c|西门子冰立方P520超氧Plus十字门冰箱|83874|
|bshcn.fridge.bva63c|西门子冰立方P520超氧Plus十字门冰箱|83872|
|bshcn.fridge.eaa22c|西门子零嵌超氧L7多门冰箱|83885|
|bshcn.fridge.eaa57c|西门子冰立方Z505超氧Lite十字门冰箱|83865|
|bshcn.fridge.eaa63c|西门子冰立方Z710超氧十字门冰箱|83866|
|bshcn.fridge.es20ti|西门子零度多门冰箱|83382|
|bshcn.fridge.fa156c|西门子保鲜大师黑钢法式多门冰箱|83284|
|bshcn.fridge.faa56c|西门子智能eNose零度多门冰箱|83291|
|bshcn.fridge.fva20c|西门子恒鲜零度多门冰箱|83290|
|bshcn.fridge.gaa20c|西门子全嵌超氧Q5十字门冰箱|84512|
|bshcn.fridge.gaa22c|西门子全嵌超氧Q7十字门冰箱|84521|
|bshcn.fridge.gaa50c|西门子全嵌超氧Q7十字门冰箱|84516|
|bshcn.fridge.gaa56c|西门子全嵌超氧Q7十字门冰箱|84514|
|bshcn.fridge.gaa61c|西门子全嵌超氧Q7十字门冰箱|84515|
|bshcn.fridge.gaa63c|西门子全嵌超氧Q5十字门冰箱|84513|
|bshcn.fridge.gaw22c|西门子全嵌超氧Q7十字门冰箱|84522|
|bshcn.fridge.gaw56c|西门子全嵌超氧Q7十字门冰箱|84523|
|bshcn.fridge.hva20c|西门子零嵌超氧L5多门冰箱|83883|
|bshcn.fridge.hva50c|西门子无界Pro超氧零度仓|83586|
|bshcn.fridge.hva56c|西门子冰立方Z505超氧Lite十字门冰箱|83867|
|bshcn.fridge.jpv50c|西门子保鲜大师黑钢冰箱|83587|
|bshcn.fridge.na236c|西门子智感零度中字门|83287|
|bshcn.fridge.naa95c|西门子智感零度冰箱|83379|
|bshcn.fridge.nade0c|西门子奢嵌L9下嵌式冰箱|84227|
|bshcn.fridge.nv141c|西门子恒鲜对开门冰箱|83292|
|bshcn.fridge.nv95t1|西门子控湿保鲜对开门|83378|
|bshcn.fridge.nva22c|西门子恒鲜对开门冰箱|83285|
|bshcn.fridge.nva63c|西门子恒鲜对开门冰箱|83289|
|bshcn.fridge.pa658c|西门子独立式超氧D9对开门冰箱|84388|
|bshcn.fridge.rade0c|西门子奢嵌L9下嵌式冰箱|84228|
|bshcn.fridge.va220c|西门子零嵌L5多门冰箱|84223|
|bshcn.fridge.va256c|西门子零嵌超氧L5多门冰箱|84220|
|bshcn.fridge.va320c|西门子超氧零度舱|83380|
|bshcn.fridge.va356c|西门子零嵌L5多门冰箱|84224|
|lge.fridge.fridge|LG无霜冷藏冷冻箱|83099|
|mibx5.fridge.bd46m|米家冰箱 对开(适用610/636L)|39072|
|midjd.fridge.256b|米家冰箱 ｜ 精巧装 三门256L 冰羽白|15602|
|midjd.fridge.439b|米家冰箱 十字439L/436L 超薄平嵌|17780|
|midjd.fridge.501b|米家冰箱 对开门501L 墨羽岩|15596|
|midjd.fridge.516|米家冰箱 十字对开门520L 墨羽岩|11149|
|midjd.fridge.603|米家冰箱 十字对开门603L 冰晶岩|13306|
|midjd.fridge.bd38l1|米家冰箱 对开门501L 墨羽岩|26804|
|midjd.fridge.bd42l|米家冰箱 对开550L/530L|28775|
|midjd.fridge.bf01l|米家冰箱｜平嵌Q7 法式439L|27689|
|midjd.fridge.bf06e|米家冰箱Pro 双系统 法式平嵌508L|30242|
|midjd.fridge.bf06s|米家冰箱Pro 双系统 法式平嵌508L|22643|
|midjd.fridge.bf06z|米家冰箱Pro 双系统 法式平嵌508L|34579|
|midjd.fridge.bf08n|米家冰箱 法式平嵌400L|36777|
|midjd.fridge.bf08s|米家冰箱 法式平嵌400L|24696|
|midjd.fridge.bf10z|米家冰箱Pro 双系统 法式平嵌508L|34575|
|midjd.fridge.bf11e|米家冰箱Pro 双系统 法式平嵌508L|28205|
|midjd.fridge.bf12l|米家冰箱Pro 双系统 法式513L|28821|
|midjd.fridge.bf12s|米家冰箱Pro 双系统 法式513L|25545|
|midjd.fridge.bf132|米家冰箱Pro 法式508L 全域离子净化4.0|37379|
|midjd.fridge.bf52a|米家冰箱Pro 微冰鲜双系统 法式平嵌560L|35956|
|midjd.fridge.bf53a|米家冰箱Pro 双系统 法式平嵌560L|33594|
|midjd.fridge.bf53s|米家冰箱Pro 双系统 法式平嵌560L 自动制冰|33590|
|midjd.fridge.bs13l|米家冰箱 十字439L/436L 超薄平嵌|27687|
|midjd.fridge.bs13s|米家冰箱 十字439L/436L 超薄平嵌|20911|
|midjd.fridge.bs19s|米家冰箱 十字430L|32298|
|midjd.fridge.bs28s1|米家冰箱 十字门（520L/501L铂银）|20990|
|midjd.fridge.bs32e|米家冰箱Pro 双系统 十字平嵌508L|30243|
|midjd.fridge.bs32s|米家冰箱Pro 双系统 十字平嵌508L|21416|
|midjd.fridge.bs41l|米家冰箱 巨能装 十字513L/十字503L|32165|
|midjd.fridge.bs42l|米家冰箱 巨能装Pro 十字513L|28773|
|midjd.fridge.bs42s|米家冰箱 巨能装Pro 十字513L|22679|
|midjd.fridge.bs42z|米家冰箱 巨能装Pro 十字513L|33019|
|midjd.fridge.bs472|米家冰箱Pro 十字508L 全域离子净化4.0|37380|
|midjd.fridge.bs52a|米家冰箱Pro 微冰鲜双系统 十字平嵌560L|35957|
|midjd.fridge.bs53a|米家冰箱Pro 双系统 十字平嵌560L|33589|
|midjd.fridge.bs53s|米家冰箱Pro 双系统 十字平嵌560L 自动制冰|33588|
|midjd.fridge.bs57s|米家冰箱Pro 双系统 十字606L/米家冰箱Pro 十字 600L|33194|
|midjd.fridge.bx27l|米家冰箱 三门271L|28097|
|midjd6.fridge.430b|米家冰箱 十字对开门430L 墨羽岩|14314|
|midjd6.fridge.430rm|米家冰箱 十字对开门430L 墨羽岩|13415|
|midjd6.fridge.540|米家冰箱 对开门540L 冰晶岩|12495|
|midjd6.fridge.540pro|米家冰箱 对开门尊享版540L|4877|
|midjd6.fridge.5501|米家冰箱 十字四门尊享版550L|4661|
|midjd6.fridge.6101|米家对开门冰箱（适用610L/606L/616L)|10777|
|midjd6.fridge.6103|米家冰箱 对开门610L 冰晶白|13488|
|midjd6.fridge.610b|米家对开门冰箱（适用610L/606L/616L）|14312|
|midjd6.fridge.s16|米家冰箱 十字518L 超薄平嵌|17836|
|midjd7.fridge.4851|米家对开门冰箱 485L|4952|
|midjd9.fridge.x14|米家冰箱 ｜ 精巧装pro 三门303L 制冰版|19336|
|minij.fridge.448w|小吉448升智能法式复古冰箱|4708|
|viomi.fridge.b1|云米互联网冰箱（对开门380L）|68138|
|viomi.fridge.b3|云米互动大屏冰箱（十字四门408L）|68897|
|viomi.fridge.b4|云米互动大屏冰箱（对开门458L）|69755|
|viomi.fridge.b5|云米冰箱21Face（十字四门451L）|70497|
|viomi.fridge.b6|云米互动大屏冰箱(对开门518L)|72074|
|viomi.fridge.b7|云米互动大屏冰箱(对开门450L)|72075|
|viomi.fridge.b9|云米互动大屏冰箱(对开门446L)云小鲜系列|72507|
|viomi.fridge.p1|云米互联网冰箱iLive（对开门 598L）|66607|
|viomi.fridge.u1|智能冰箱iLive|442|
|viomi.fridge.u12|云米互联网冰箱 十字四门398/415L 定频|66555|
|viomi.fridge.u13|云米互联网冰箱 十字四门415L/416L|66552|
|viomi.fridge.u15|云米互联网冰箱iLive（法式 365L）|66775|
|viomi.fridge.u17|云米互联网冰箱 十字四门398/415L|67261|
|viomi.fridge.u18|云米互联网冰箱iLive（对开门 485L）|67512|
|viomi.fridge.u2|云米互联网冰箱iLive 对开门版|729|
|viomi.fridge.u24|云米互联网冰箱（对开门450L）|68989|
|viomi.fridge.u25|云米互联网冰箱（法式345L）|68990|
|viomi.fridge.u26|云米冰箱iLive（对开门552L）|69186|
|viomi.fridge.u28|云米冰箱iLive（十字四门450L）|69385|
|viomi.fridge.u29|云米冰箱iLive（法式355L）|69387|
|viomi.fridge.u30|云米冰箱iLive（对开门566L）|69388|
|viomi.fridge.u31|云米冰箱iLive（十字四门508L）|69626|
|viomi.fridge.u32|云米冰箱iLive（对开门456L）|70031|
|viomi.fridge.u34|云米冰箱iLive（对开门640L）|70059|
|viomi.fridge.u35|云米冰箱iLive（十字四门410L）|70060|
|viomi.fridge.u36|云米互联网冰箱iLive（十字四门506L）|70061|
|viomi.fridge.u37|云米互联网冰箱iLive（对开门 528L）|70373|
|viomi.fridge.u38|云米互联网冰箱iLive（对开门 568L）|70424|
|viomi.fridge.u39|云米冰箱iLive2（十字四门485L）|70832|
|viomi.fridge.u4|云米互联网冰箱对开门ilive 483L|65759|
|viomi.fridge.u40|云米冰箱iLive（法式四门416L）|70833|
|viomi.fridge.u41|云米互联网冰箱iLive2(对开门639L)|71503|
|viomi.fridge.u42|云米互联网冰箱iLive2(十字门509L)|71504|
|viomi.fridge.u43|云米互联网冰箱iLive2(法式四门445L)|71505|
|viomi.fridge.u44|云米互联网冰箱iLive2(十字四门513L)|71506|
|viomi.fridge.u45|云米互联网冰箱iLive2(法式四门508L)|71507|
|viomi.fridge.u46|云米互联网冰箱iLive(对开门456L)升级版|4319|
|viomi.fridge.u47|云米互联网冰箱iLive2(对开门590L)|4432|
|viomi.fridge.u49|云米AI智能冰箱iLive2(十字四门450L)语音版|6317|
|viomi.fridge.u50|云米AI智能冰箱iLive2(十字四门518L)语音版|6319|
|viomi.fridge.u51|云米AI智能冰箱iLive2(对开门636L)|6465|
|viomi.fridge.u55|云米AI冰箱Cross E(对开646)|12051|
|viomi.fridge.u56|云米AI冰箱Smart E（十字412）|12432|
|viomi.fridge.u57|云米互联网冰箱iLive（对开456）|12579|
|viomi.fridge.u58|云米AI冰箱Smart E(对开456)|13132|
|viomi.fridge.u6|云米互联网冰箱ilive十字四门486L|65973|
|viomi.fridge.u60|云米AI冰箱Master 3Y（十字536）|13394|
|viomi.fridge.u62|云米AI冰箱Super 2S（对开550）|13878|
|viomi.fridge.u64|云米AI冰箱Smart E(对开456)|15074|
|viomi.fridge.u68|云米AI冰箱Master 3(法式400)|17522|
|viomi.fridge.u69|云米AI冰箱Super 2Pro(十字502)|17794|
|viomi.fridge.u7|云米互联网冰箱ilive 对开门545L|65974|
|viomi.fridge.u70|云米AI冰箱Super 2S(法式509)|17798|
|viomi.fridge.u71|云米AI冰箱Super 2S(十字508)|17869|
|viomi.fridge.u73|云米AI冰箱Master 3E（十字520）|20062|
|viomi.fridge.u8|云米互联网冰箱iLive（对开门 603L）|66058|
|viomi.fridge.v3|云米智能冰箱法式 iLive语音版|645|
|viomi.fridge.w1|云米互联网冰箱 iLive2（三门 301L）|587|
|viomi.fridge.w2|云米互联网冰箱 iLive2（双门 272L）|705|
|viomi.fridge.x11|云米互联网冰箱21Face (对开门 525L)|67400|
|viomi.fridge.x12|云米互联网冰箱21Face（T型三门 408L）|67498|
|viomi.fridge.x13|云米冰箱21Face（法式520L）|68714|
|viomi.fridge.x14|云米冰箱21Face（十字四门516L）|68715|
|viomi.fridge.x15|云米冰箱21Face (对开门522L)|69184|
|viomi.fridge.x17|云米冰箱21Face（对开门450L）|69417|
|viomi.fridge.x19|云米冰箱21Face（对开门635L）|70062|
|viomi.fridge.x20|云米冰箱21Face（十字四门502L）|70063|
|viomi.fridge.x21|云米冰箱21Face (对开门630L)|70756|
|viomi.fridge.x22|云米冰箱 21Face (法式510L)|70350|
|viomi.fridge.x23|云米冰箱21Face（十字四门510L）|70459|
|viomi.fridge.x24|云米冰箱21Face（法式四门 516L）|70685|
|viomi.fridge.x25|云米冰箱21Face（对开门456L）|70686|
|viomi.fridge.x26|云米冰箱YMDK01|71000|
|viomi.fridge.x28|云米冰箱21Face(十字四门502L)|71073|
|viomi.fridge.x29|云米冰箱21Face（法式四门505L）|71074|
|viomi.fridge.x35|云米互联网冰箱21Face(对开门610L)|72282|
|viomi.fridge.x37|云米AI冰箱21Face2(对开门525L)智目版|72775|
|viomi.fridge.x38|云米AI冰箱21Face2(十字四门506L)智目版|72776|
|viomi.fridge.x4|云米互联网冰箱21Face(对开门450L)|787|
|viomi.fridge.x44|云米AI智能冰箱21Face2(对开门525L)智目版|73596|
|viomi.fridge.x48|云米AI冰箱21Face 2S(对开640)|75100|
|viomi.fridge.x49|云米AI冰箱21Face 2S(十字502)|75101|
|viomi.fridge.x50|云米AI冰箱21Face 2PRO(T型门515）|75169|
|viomi.fridge.x7|云米互联网冰箱21Face（428L）|66684|
|xckj.fridge.111wg2|圈厨111L家用智能冰柜|69537|
|xckj.fridge.151wg1|圈厨家用智能冰柜|68068|
|xckj.fridge.448ws4|圈厨梵希法式四门冰箱|67775|
|xxll.fridge.mtb40g|星星智能冰柜|17905|

### 洗衣机：70/239，缺 169

|model|name|pd_id|
|---|---|---:|
|bshcn.washer.0au00w|博世壁挂式迷你洗衣机|84251|
|bshcn.washer.2j5000|西门子iQ300洗干一体机|83689|
|bshcn.washer.2j5080|西门子iQ300洗干一体机|83685|
|bshcn.washer.2j7i00|西门子iQ300洗干一体机|83690|
|bshcn.washer.2j7i10|西门子iQ300洗干一体机|83694|
|bshcn.washer.2j7i80|西门子iQ300洗干一体机|83695|
|bshcn.washer.4d3a10|西门子iQ500洗干一体机12kg|83224|
|bshcn.washer.4j7i10|西门子iQ300洗衣机|84646|
|bshcn.washer.52000w|博世4系洗衣机|83537|
|bshcn.washer.52010w|博世4系洗衣机|83533|
|bshcn.washer.52080w|博世4系洗衣机|83539|
|bshcn.washer.52i00w|博世4系洗干一体机|83697|
|bshcn.washer.52i10w|博世4系洗衣机|84847|
|bshcn.washer.52j7i8|西门子iQ300洗衣机|84064|
|bshcn.washer.52j7y0|西门子iQ300洗衣机|84063|
|bshcn.washer.52j7y1|西门子iQ300洗衣机|84065|
|bshcn.washer.52y00w|博世摩德纳洗衣机|83550|
|bshcn.washer.52y10w|博世摩德纳洗衣机|83549|
|bshcn.washer.52y60w|博世摩德纳洗衣机|83545|
|bshcn.washer.52y80w|博世摩德纳洗衣机|83554|
|bshcn.washer.54b01w|博世6系洗衣机|83255|
|bshcn.washer.54b0hw|博世6系洗衣机|83260|
|bshcn.washer.54b8hw|博世6系洗衣机|83256|
|bshcn.washer.54b9hw|博世6系洗衣机|83259|
|bshcn.washer.54c00w|博世6系洗衣机|83261|
|bshcn.washer.54c10w|博世6系洗衣机|83257|
|bshcn.washer.54c31w|博世8系洗衣机|84253|
|bshcn.washer.54d00w|博世摩德纳洗衣机|83112|
|bshcn.washer.54d01w|博世6系洗衣机|84807|
|bshcn.washer.54d10w|博世摩德纳洗衣机|83449|
|bshcn.washer.54d20w|博世大师洗衣机|83526|
|bshcn.washer.54d50w|博世大师洗衣机|83528|
|bshcn.washer.54d51w|博世6系洗衣机|84805|
|bshcn.washer.54d60w|博世摩德纳洗衣机|83452|
|bshcn.washer.54d80w|博世摩德纳洗衣机|83450|
|bshcn.washer.54f20w|博世4系洗衣机|84059|
|bshcn.washer.54g10w|博世6系洗干一体机|83686|
|bshcn.washer.552y00|博世4系洗衣机|83849|
|bshcn.washer.56b00w|博世8系进口洗衣机|84392|
|bshcn.washer.56g20w|博世6系洗干一体机|84067|
|bshcn.washer.74d20w|博世8系洗衣机|84743|
|bshcn.washer.74f80w|博世6系洗衣机|84647|
|bshcn.washer.752y00|博世4系洗衣机|84061|
|bshcn.washer.752y10|博世4系洗衣机|84060|
|bshcn.washer.754d00|博世大师洗衣机|83529|
|bshcn.washer.754d60|博世大师洗衣机|83530|
|bshcn.washer.8560hw|博世6系洗衣机|83258|
|bshcn.washer.a6b00w|西门子iQ800洗衣机|83444|
|bshcn.washer.b2b00w|西门子iQ700进口洗衣机|84391|
|bshcn.washer.c2b0hw|西门子iQ500洗衣机|83254|
|bshcn.washer.c3b8hw|西门子iQ500洗衣机|83252|
|bshcn.washer.c5a10w|西门子iQ500洗干一体机|83425|
|bshcn.washer.c5c10w|西门子iQ500洗衣机|83098|
|bshcn.washer.c5c80w|西门子iQ500洗衣机|83139|
|bshcn.washer.c8c11w|西门子iQ700洗衣机|84252|
|bshcn.washer.d3b10w|西门子iQ500洗衣机|83445|
|bshcn.washer.f7f20w|西门子包豪斯洗衣机|83531|
|bshcn.washer.j5000w|西门子iQ300洗衣机|83534|
|bshcn.washer.j5080w|西门子iQ300洗衣机|83535|
|bshcn.washer.j552y0|博世4系洗衣机|84062|
|bshcn.washer.j7a10w|西门子小幸熨洗衣机|83548|
|bshcn.washer.j7a80w|西门子小幸熨洗衣机|83552|
|bshcn.washer.j7i00w|西门子小幸熨洗衣机|83543|
|bshcn.washer.j7i10w|西门子小幸熨洗衣机|83542|
|bshcn.washer.j7i80w|西门子小幸熨洗衣机|83553|
|bshcn.washer.j7y00w|西门子小幸熨洗衣机|83540|
|bshcn.washer.j7y10w|西门子小幸熨洗衣机|83546|
|bshcn.washer.j7y70w|西门子小幸熨洗衣机|83547|
|bshcn.washer.j7y81w|西门子小幸熨洗衣机|83551|
|bshcn.washer.k7d00w|西门子小幸熨洗衣机|83140|
|bshcn.washer.k7d10w|西门子iQ500超氧洗衣机|82160|
|bshcn.washer.k7d11w|西门子iQ500洗衣机|84254|
|bshcn.washer.k7d29w|西门子小幸熨洗衣机|83451|
|bshcn.washer.k7d70w|西门子小幸熨洗衣机|83453|
|bshcn.washer.k7d80w|西门子小幸熨洗衣机|83448|
|bshcn.washer.k7g00w|西门子iQ500洗干一体机|83701|
|bshcn.washer.k7g10w|西门子iQ500洗干一体机|83603|
|bshcn.washer.k7g80w|西门子iQ500洗干一体机|83687|
|bshcn.washer.m7d10w|西门子包豪斯洗衣机|83525|
|bshcn.washer.m7d20w|西门子包豪斯洗衣机|83454|
|bshcn.washer.m7d29w|西门子iQ500洗衣机|84804|
|bshcn.washer.m7d71w|西门子iQ500洗衣机|84806|
|bshcn.washer.m7d80w|西门子包豪斯洗衣机|83527|
|bshcn.washer.m7g20w|西门子iQ500洗干一体机|84066|
|bshcn.washer.p5y70w|西门子iQ300洗衣机|84854|
|bshcn.washer.p752y1|博世4系洗衣机|84803|
|bshcn.washer.p7d20w|西门子iQ700洗衣机|84648|
|bshcn.washer.u561hw|西门子iQ500洗衣机|83263|
|bshcn.washer.u5x8hw|西门子iQ500洗干一体机|83298|
|bshcn.washer.u7b1hw|西门子iQ500洗衣机|83253|
|bshcn.washer.w6600w|西门子iQ800洗衣机|83447|
|bshcn.washer.w7010w|西门子壁挂式迷你洗衣机|83481|
|bshcn.washer.ws52j7|西门子iQ300洗干一体机|84845|
|lge.washer.washer|LG全自动滚筒洗衣机|83100|
|mibx2.washer.v1|米家互联网直驱洗烘一体机 10kg|2764|
|mibx2.washer.v11|米家直驱洗烘一体机 10kg|9381|
|mibx2.washer.v13|米家Mini洗衣机 1kg|10402|
|mibx2.washer.v15rm|米家洗烘一体机 12kg/11.8kg 钛金灰|13456|
|mibx2.washer.v2|米家直驱洗烘一体机 10kg|4466|
|mibx2.washer.v3|米家波轮洗衣机 10kg|4499|
|mibx2.washer.v7|直驱｜米家洗烘一体机 尊享版10kg|6536|
|mibx5.washer.32|米家洗衣机 ｜ 超净洗 滚筒10kg|15732|
|mibx5.washer.35|米家洗衣机 超净洗 洗烘10kg|15733|
|mibx5.washer.f52|米家洗衣机 洗烘12kg|25871|
|mibx5.washer.f521|米家洗衣机 洗烘12kg|26807|
|mibx5.washer.f56|米家洗衣机Pro 蓝氧 洗烘10kg|24378|
|mibx5.washer.f60|米家洗衣机Pro 蓝氧 洗烘12kg|25872|
|mibx5.washer.f69|米家洗衣机Pro 超电解智投 滚筒12kg|28149|
|mibx5.washer.f81|米家洗衣机 滚筒12kg|30334|
|mibx5.washer.f91|米家洗衣机 滚筒12kg|33884|
|mibx5.washer.s06|米家洗衣机Pro 迷你3kg|19597|
|mibx5.washer.s12|米家洗衣机Pro 智投 迷你3kg|24529|
|mibx5.washer.v14|直驱 / 米家滚筒洗衣机 10kg|14643|
|mibx5.washer.v4|直驱 / 米家滚筒洗衣机 尊享版 10kg|5290|
|mibx5.washer.x061|米家双区洗衣机 滚筒10kg|31160|
|midjd4.washer.s08|米家洗衣机 迷你洗 洗烘|20414|
|midjd8.washer.42|米家洗衣机 超净洗Pro 洗烘12kg|16065|
|midjd8.washer.44|米家洗衣机 ｜ 超净洗Pro 洗烘一体10kg|16023|
|miele.washer.w001|美诺洗衣机|83071|
|minij.washer.v1|小吉智能迷你滚筒洗衣机|165|
|minij.washer.v12|小吉智能水珠壁挂洗衣机|1299|
|minij.washer.v15|小吉智能迷你滚筒洗衣机2.8kg|1345|
|minij.washer.v17|小吉智能壁挂洗烘一体机|1927|
|minij.washer.v27|米家互联网迷你波轮洗衣机Pro 3kg|8600|
|moyu.washer.dg02|摩鱼内衣洗护机dg02|17161|
|moyu.washer.dg08|摩鱼内衣洗护机dg08|17162|
|moyu.washer.s1hm|摩鱼智能母婴洗衣机|65627|
|viomi.washer.s1|云米互联网波轮洗衣机（9KG）|66504|
|viomi.washer.sd10|云米AI洗烘一体机 Super 2 Max (12KG)|13396|
|viomi.washer.sd11|云米AI洗衣机Super 2E（10Kg DD直驱）|13916|
|viomi.washer.sd13|云米AI洗烘一体机Super 2Pro(10kg新风滚筒)|15369|
|viomi.washer.sd14|云米AI洗烘机 Super 2S(10kg全嵌智投）|17824|
|viomi.washer.sd15|云米AI洗烘机 Master 3E（10kg全嵌智投）|24302|
|viomi.washer.u1|云米洗衣机（9kg/10kg语音版）|640|
|viomi.washer.u2|云米互联网洗烘一体机|872|
|viomi.washer.u3|云米互联网洗衣机（8KG）|65800|
|viomi.washer.u4|云米互联网洗衣机（10KG）|65801|
|viomi.washer.u5|云米洗烘一体机（10kg语音版）|953|
|viomi.washer.v10|云米互联网洗烘一体机（8kg尊享版）|67179|
|viomi.washer.v11|云米互联网洗烘一体机（10kg尊享版）|67178|
|viomi.washer.v13|云米洗烘一体机Neo（10kg）|68066|
|viomi.washer.v14|云米洗衣机Neo（10kg）|68067|
|viomi.washer.v17|云米互联网洗烘一体机Eyebot|68982|
|viomi.washer.v18|云米互联网洗烘机EyeBot Face新风速烘11kg|68983|
|viomi.washer.v19|云米洗烘一体机Neo（10kg直驱版）|69181|
|viomi.washer.v20|云米洗烘一体机（10kg领航版/智航版）|69182|
|viomi.washer.v21|云米洗衣机（10kg领航版/智航版）|69183|
|viomi.washer.v22|coKiing AI洗烘一体机Royal(智能投放版)|69931|
|viomi.washer.v23|云米互联网洗衣机Master（8KG）|70400|
|viomi.washer.v24|云米互联网洗衣机Master（10KG）|70401|
|viomi.washer.v25|云米互联网洗烘一体机Master（10KG）|70402|
|viomi.washer.v26|云米互联网洗烘一体机Neo2Pro(10kg DD直驱)|70737|
|viomi.washer.v27|云米互联网洗衣机Neo2Pro(10kg DD直驱)|70738|
|viomi.washer.v28|云米互联网洗烘一体机Neo2(10kg 智能投放)|70739|
|viomi.washer.v32|云米互联网洗衣机EyeBot(12KG 智目洗版)|71194|
|viomi.washer.v33|云米互联网洗烘机Master 2 智能投放 10kg|4311|
|viomi.washer.v34|云米互联网洗烘机Master 2S 紫外除菌 10kg|4313|
|viomi.washer.v35|云米互联网洗烘机Master 2PRO 蒸汽护理10kg|4314|
|viomi.washer.v36|云米互联网洗烘机Neo2S 紫外除菌 10kg|4317|
|viomi.washer.v38|云米互联网洗烘机Master 2Mix 智目版 10kg|4569|
|viomi.washer.v4|云米互联网洗烘一体机（8KG乐享版）|66521|
|viomi.washer.v40|云米互联网洗烘机Neo3 智目版 10kg|4571|
|viomi.washer.v41|云米AI洗烘机 新风速烘版 10kg|4572|
|viomi.washer.v46|云米互联网洗烘机Neo2S 紫外除菌 10kg|9132|
|viomi.washer.v5|云米互联网洗烘一体机（10KG乐享版）|66790|
|viomi.washer.v6|云米互联网洗烘一体机Rose 9kg|66789|
|viomi.washer.v7|云米互联网洗烘一体机Neo（8kg OTA版）|67003|
|viomi.washer.v8|云米互联网洗烘一体机Neo（10kg OTA版）|67002|
|viomi.washer.w1|云米互联网壁挂洗衣机 小新|70007|

### 微波炉：5/7，缺 2

|model|name|pd_id|
|---|---|---:|
|chunmi.microwave.n20l02|米家微波炉|5753|
|chunmi.microwave.n23l01|米家智能微烤一体机|2442|

### 洗碗机：22/161，缺 139

|model|name|pd_id|
|---|---|---:|
|bshcn.dishwasher.23eb33|西门子极净魔盒新一级水效智能烘干洗碗机|83900|
|bshcn.dishwasher.25zb24|西门子智净魔方晶蕾洗碗机|83063|
|bshcn.dishwasher.3eb24k|西门子智净魔方洗碗机|84384|
|bshcn.dishwasher.43eb33|智净魔方灶下洗碗机|83664|
|bshcn.dishwasher.43hb25|智净魔方洗碗机|83517|
|bshcn.dishwasher.4ekb88|博世小虎鲸独嵌两用洗碗机|83668|
|bshcn.dishwasher.5zx26m|西门子智净魔方Pro洗碗机|84421|
|bshcn.dishwasher.63hx00|西门子全能舱洗碗机|83047|
|bshcn.dishwasher.65zx00|智净魔方Pro洗碗机|83409|
|bshcn.dishwasher.6mx16c|博世嵌入式洗碗机|83407|
|bshcn.dishwasher.6x26jc|西门子晶蕾洗碗机|83043|
|bshcn.dishwasher.75zx00|西门子全能舱晶蕾洗碗机|83051|
|bshcn.dishwasher.8ix06c|博世6系嵌入式洗碗机|83055|
|bshcn.dishwasher.8s06jc|西门子晶蕾洗碗机|83042|
|bshcn.dishwasher.eb06kc|西门子黑魔镜U7智能烘干洗碗机|83897|
|bshcn.dishwasher.eb11kc|西门子极净魔盒洗碗机|83131|
|bshcn.dishwasher.eb11mc|极净魔盒3.0洗碗机|83510|
|bshcn.dishwasher.eb18mc|西门子极净魔盒新一级水效智能烘干洗碗机|83899|
|bshcn.dishwasher.eb20mc|西门子极净魔盒6.0洗碗机|84670|
|bshcn.dishwasher.eb21mc|西门子极净魔盒6.0洗碗机|84671|
|bshcn.dishwasher.eb24kc|智净魔方Auto洗碗机|83511|
|bshcn.dishwasher.eb26kc|西门子全能舱U7洗碗机|84383|
|bshcn.dishwasher.eb26mc|西门子极净魔盒6.0洗碗机|84672|
|bshcn.dishwasher.eb33kc|西门子全能舱Auto洗碗机|83060|
|bshcn.dishwasher.eb33mc|西门子全能舱Auto洗碗机|83129|
|bshcn.dishwasher.eb63mc|西门子黑魔镜新一级水效智能烘干洗碗机|83898|
|bshcn.dishwasher.eb88kc|极净魔盒3.0洗碗机|83417|
|bshcn.dishwasher.eb88mc|极净魔盒3.0洗碗机|83516|
|bshcn.dishwasher.eb99kc|极净魔盒3.0洗碗机|83415|
|bshcn.dishwasher.ekb11c|博世4系独嵌两用洗碗机|83138|
|bshcn.dishwasher.ekb88c|博世小虎鲸嵌入式洗碗机|83136|
|bshcn.dishwasher.ekw88c|博世小虎鲸嵌入式洗碗机|83133|
|bshcn.dishwasher.ekx00c|博世4系嵌入式洗碗机|83053|
|bshcn.dishwasher.emb99c|博世嵌入式洗碗机|83669|
|bshcn.dishwasher.emw99c|博世小虎鲸嵌入式洗碗机|83666|
|bshcn.dishwasher.es23kc|西门子灶下洗碗机|83130|
|bshcn.dishwasher.ew88kc|极净魔盒3.0洗碗机|83416|
|bshcn.dishwasher.ex00kc|西门子全能舱Auto洗碗机|83036|
|bshcn.dishwasher.ex66kc|西门子隐嵌开门烘干洗碗机|83670|
|bshcn.dishwasher.hb00kc|西门子全能舱洗碗机|83035|
|bshcn.dishwasher.hb03mc|西门子黑魔镜636双核热动力烘干洗碗机|83892|
|bshcn.dishwasher.hb06mc|西门子极净魔盒3.0双核热动力烘干洗碗机|83894|
|bshcn.dishwasher.hb08kc|西门子全能舱洗碗机|83137|
|bshcn.dishwasher.hb11kc|西门子全能舱洗碗机|83052|
|bshcn.dishwasher.hb11mc|西门子极净魔盒Plus洗碗机|83128|
|bshcn.dishwasher.hb24mc|西门子智净魔方洗碗机|83062|
|bshcn.dishwasher.hb25kc|智净魔方灶下洗碗机|83662|
|bshcn.dishwasher.hb25mc|西门子智净魔方洗碗机|83132|
|bshcn.dishwasher.hb55kc|智净魔方灶下洗碗机|83660|
|bshcn.dishwasher.hb66mc|智净魔方洗碗机|83521|
|bshcn.dishwasher.hb88mc|西门子全能舱洗碗机|83050|
|bshcn.dishwasher.hi88mc|西门子全能舱洗碗机|83048|
|bshcn.dishwasher.hkb99c|博世V10灶下新风洗碗机|83514|
|bshcn.dishwasher.hks66c|博世4系嵌入式洗碗机|83056|
|bshcn.dishwasher.hl24mc|西门子下嵌式智能洗碗机|82152|
|bshcn.dishwasher.hl25kc|智净魔方灶下洗碗机|83512|
|bshcn.dishwasher.hl25mc|智净魔方洗碗机|83509|
|bshcn.dishwasher.hl66mc|智净魔方洗碗机|83518|
|bshcn.dishwasher.hmb66c|博世V10嵌入式洗碗机|83135|
|bshcn.dishwasher.hmb99c|博世V10Pro嵌入式洗碗机|83134|
|bshcn.dishwasher.hmx66c|博世V10 Pro新风洗碗机|83513|
|bshcn.dishwasher.hs00kc|西门子全能舱洗碗机|83049|
|bshcn.dishwasher.hs11mc|智净魔方洗碗机|83519|
|bshcn.dishwasher.ht66mc|智净魔方洗碗机|83520|
|bshcn.dishwasher.hx66mc|智净魔方洗碗机|83663|
|bshcn.dishwasher.sn75zx|智净魔方Pro洗碗机|83412|
|bshcn.dishwasher.vb26mc|西门子极净魔盒6.0洗碗机|84673|
|bshcn.dishwasher.vmw06c|博世V20 Pro焕彩版洗碗机|84674|
|bshcn.dishwasher.x00mc|西门子全能舱晶蕾洗碗机|83034|
|bshcn.dishwasher.xb33kc|西门子极净魔盒洗碗机|83046|
|bshcn.dishwasher.y80pcc|西门子智净魔方Pro进口洗碗机|84455|
|bshcn.dishwasher.yc80pc|博世天工系列进口沸石洗碗机|84456|
|bshcn.dishwasher.zb11mc|智净魔方Plus洗碗机|83413|
|bshcn.dishwasher.zb24mc|西门子智净魔方晶蕾洗碗机|83037|
|bshcn.dishwasher.zb25kc|西门子极净魔盒灶下晶蕾洗碗机|83061|
|bshcn.dishwasher.zb26mc|西门子智净魔方Pro洗碗机|84423|
|bshcn.dishwasher.zb28mc|智净魔方Pro洗碗机|83503|
|bshcn.dishwasher.zb29mc|西门子智净魔方Pro洗碗机|84420|
|bshcn.dishwasher.zb58kc|西门子智净魔方灶下新一级水效晶蕾烘干洗碗机|83901|
|bshcn.dishwasher.zb66kc|西门子智净魔方U7 Plus洗碗机|84460|
|bshcn.dishwasher.zb66mc|西门子智净魔方Plus洗碗机|84662|
|bshcn.dishwasher.zb69kc|西门子智净魔方U7 Plus洗碗机|84459|
|bshcn.dishwasher.zb69mc|西门子智净魔方Plus洗碗机|84663|
|bshcn.dishwasher.zb88kc|西门子灶下晶蕾洗碗机|83033|
|bshcn.dishwasher.zb88mc|智净魔方Plus洗碗机|83400|
|bshcn.dishwasher.zb99mc|智净魔方Pro洗碗机|83411|
|bshcn.dishwasher.zc06mc|西门子智净魔方Pro晶蕾烘干洗碗机|83896|
|bshcn.dishwasher.zc25kc|智净魔方灶下洗碗机|83403|
|bshcn.dishwasher.zc66mc|西门子智净魔方Plus洗碗机|84664|
|bshcn.dishwasher.zcz66c|博世进口6系嵌入式洗碗机|83408|
|bshcn.dishwasher.zkc00c|博世Z10灶下沸石洗碗机|83507|
|bshcn.dishwasher.zkx26c|博世Z20灶下沸石洗碗机|84427|
|bshcn.dishwasher.zl24mc|西门子智净魔方Pro洗碗机|84381|
|bshcn.dishwasher.zl26kc|西门子智净魔方U7 Plus洗碗机|84458|
|bshcn.dishwasher.zl26mc|西门子智净魔方Pro洗碗机|84422|
|bshcn.dishwasher.zl66mc|西门子智净魔方Plus洗碗机|84665|
|bshcn.dishwasher.zmb11c|博世Z10 Plus沸石洗碗机|83502|
|bshcn.dishwasher.zmb16c|博世Z20 Plus沸石洗碗机|84669|
|bshcn.dishwasher.zmb26c|博世Z20 Pro沸石洗碗机|84424|
|bshcn.dishwasher.zmb66c|博世Z10洗碗机|84382|
|bshcn.dishwasher.zmb99c|博世Z10 Pro沸石洗碗机|83414|
|bshcn.dishwasher.zmc00c|博世Z10 Pro沸石洗碗机|83504|
|bshcn.dishwasher.zmx00c|博世6系嵌入式洗碗机|83054|
|bshcn.dishwasher.zmx01c|博世Z10 Plus洗碗机|83659|
|bshcn.dishwasher.zmx11c|博世Z10 嵌入式洗碗机|83111|
|bshcn.dishwasher.zmx26c|博世Z20 Pro沸石洗碗机|84425|
|bshcn.dishwasher.zmx66c|博世Z10 Pro 新一级水效沸石烘干洗碗机|83903|
|bshcn.dishwasher.zmx99c|博世Z10 Pro灵动大师沸石洗碗机|83506|
|bshcn.dishwasher.zs11mc|智净魔方Plus洗碗机|83515|
|bshcn.dishwasher.zx06mc|西门子黑魔镜65ZPro晶蕾烘干洗碗机|83895|
|bshcn.dishwasher.zx08mc|智净魔方Pro洗碗机|83402|
|bshcn.dishwasher.zx11mc|智净魔方Plus洗碗机|83508|
|bshcn.dishwasher.zx26mc|西门子智净魔方Pro新一级水效晶蕾烘干洗碗机|83902|
|bshcn.dishwasher.zx28mc|智净魔方Pro洗碗机|83410|
|bshcn.dishwasher.zx55mc|西门子智净魔方Plus洗碗机|84666|
|bshcn.dishwasher.zx66kc|西门子智净魔方U7 Plus洗碗机|84461|
|bshcn.dishwasher.zx66mc|西门子智净魔方Plus洗碗机|84667|
|bshcn.dishwasher.zx68kc|西门子智净魔方U7 Plus洗碗机|84426|
|bshcn.dishwasher.zx68mc|西门子智净魔方Plus洗碗机|84668|
|bshcn.dishwasher.zx88mc|智净魔方Plus洗碗机|83401|
|hzft.dishwasher.vp10|方太智能洗碗机|81748|
|miele.dishwasher.w001|美诺洗碗机|83072|
|msj.dishwasher.s02|美仕杰集成水槽星云款|12327|
|msj.dishwasher.s110u|美仕杰家用集成水槽|17837|
|viomi.dishwasher.v01|云米互联网洗碗机（8套嵌入式）|672|
|viomi.dishwasher.v03|云米互联网洗碗机（嵌入式）|66386|
|viomi.dishwasher.v05|云米互联网水槽洗碗机|67211|
|viomi.dishwasher.v06|云米互联网洗碗机（嵌入式）|68737|
|viomi.dishwasher.v08|云米互联网洗碗机嵌入式0803A|69771|
|viomi.dishwasher.v09|云米互联网洗碗机4套台面式0402|70264|
|viomi.dishwasher.v10|云米互联网洗碗机10套嵌入式0805|70751|
|viomi.dishwasher.v11|云米互联网洗碗机10套嵌入式0804|71003|
|viomi.dishwasher.v12|云米互联网洗碗机嵌入式0803B|71689|
|viomi.dishwasher.v14|云米互联网洗碗机10套嵌入式0807|4687|
|viomi.dishwasher.v15|云米AI洗碗机Milano 15套|7090|
|viomi.dishwasher.v17|云米AI洗碗机Super|8066|
|wanhe.dishwasher.x60|万和洗碗机|83955|
|xckj.dishwasher.idw01|圈厨嵌入式互联网洗碗机|68204|
|zjyg.dishwasher.zzy01|智能烘洗式洗碗机|67994|

### 电热水器：7/48，缺 41

|model|name|pd_id|
|---|---|---:|
|macro.waterheater.w9|万家乐储水式电热水器|83761|
|smith.waterheater.cxea1|佳尼特电热水器CXE-A1|66988|
|smith.waterheater.cxeb1|佳尼特电热水器CXE-60B1|66987|
|smith.waterheater.x1|佳尼特电热水器CTE-X1|5109|
|vatti.waterheater.dj10|华帝电热水器DJ10|14692|
|vatti.waterheater.ds9|华帝电热水器DS9|14691|
|vatti.waterheater.yp07i|华帝电热水器DJ9|12715|
|viomi.waterheater.e1|云米互联网电热水器1A（60L）|65820|
|viomi.waterheater.e13|云米互联网免更换镁棒电热水器 50L|67746|
|viomi.waterheater.e14|云米互联网免更换镁棒电热水器 60L|67745|
|viomi.waterheater.e15|云米互联网免更换镁棒电热水器 80L|67744|
|viomi.waterheater.e16|云米互联网电热水器C1（50L）|68941|
|viomi.waterheater.e17|云米互联网电热水器C1（60L）|68942|
|viomi.waterheater.e19|云米互联网电热水器VEW5015|70247|
|viomi.waterheater.e20|云米互联网电热水器VEW6015|70248|
|viomi.waterheater.e21|云米互联网电热水器VEW5016|70249|
|viomi.waterheater.e22|云米互联网电热水器VEW6016|70250|
|viomi.waterheater.e24|云米互联网电热水器VEW5018|71792|
|viomi.waterheater.e25|云米互联网电热水器VEW6018|71793|
|viomi.waterheater.e26|云米互联网电热水器VEW5019|71794|
|viomi.waterheater.e27|云米互联网电热水器VEW6019|71795|
|viomi.waterheater.e28|云米AI电热水器VEW5020|71796|
|viomi.waterheater.e29|云米AI电热水器VEW6020|71797|
|viomi.waterheater.e3|云米互联网电热水器Air（60L双胆语音）|66187|
|viomi.waterheater.e33|云米AI电热水器VEW6022|5150|
|viomi.waterheater.e38|云米AI电热水器小蓝调|8935|
|viomi.waterheater.e4|云米互联网电热水器50L（优享版）|66188|
|viomi.waterheater.e42|蓝调智能电热水器|9275|
|viomi.waterheater.e44|云米AI电热水器 Air 双胆优享版|10487|
|viomi.waterheater.e45|云米AI电热水器 Super|10488|
|viomi.waterheater.e47|云米AI电热水器Smart 2|12730|
|viomi.waterheater.e48|云米AI电热水器Super 2 Pro|13338|
|viomi.waterheater.e49|云米AI电热水器 Smart E|17022|
|viomi.waterheater.e50|云米AI电热水器 Super 3|21622|
|viomi.waterheater.e7|云米互联网电热水器Air（60L 双胆优享版）|66606|
|viomi.waterheater.e8|云米互联网电热水器Air（60L双胆智享版）|66605|
|wanhe.waterheater.a6pro|万和电热水器出水断电款|82207|
|wanhe.waterheater.q2|万和电热水器智能款|82253|
|xckj.waterheater.int01|圈厨超薄互联网电热水器50L|68203|
|xckj.waterheater.int02|圈厨超薄互联网电热水器60L|69123|
|yunmi.waterheater.e51|云米AI双胆电热水器 蓝调2|25993|

### 风扇：31/171，缺 140

|model|name|pd_id|
|---|---|---:|
|air.fan.ca23ad9|艾美特空气循环扇|66514|
|als1.fan.j15pm|科宾斯智能风扇J15-Pro max|35127|
|als1.fan.j15sl|双鹿智能风扇J15-Pro max|36581|
|als1.fan.j5kbs|科宾斯智能风扇J5 Pro Max|36933|
|als1.fan.j5sl|双鹿智能风扇J5 Pro Max|36997|
|als1.fan.j5yyz|优越者智能风扇Y5 Pro Max|36838|
|als1.fan.j90pm|科宾斯智能风扇J90-Pro max|34844|
|als1.fan.j90sl|双鹿智能风扇J90-Pro max|36110|
|als1.fan.jz5|优越者智能风扇Y90-Pro max|34616|
|als1.fan.jz8x|科宾斯智能风扇Z9-Pro max|34846|
|als1.fan.kbsz5|科宾斯智能风扇Z5-Pro max|35973|
|als1.fan.xkz5p|昕科智能风扇Z5 Pro Max|37197|
|als1.fan.y15pm|优越者智能风扇Y15-Pro max|35195|
|als1.fan.y9pm|优越者智能风扇Y9-Pro max|35446|
|als1.fan.z5sl|双鹿智能风扇Z5 Pro Max|36263|
|als1.fan.z5yyz|优越者智能风扇Z5 Pro Max|36932|
|als1.fan.z9sl|双鹿智能风扇Z9-Pro max|36157|
|amdq.fan.amfs|爱亿馨空气循环扇|26319|
|bm6688.fan.002|米可白蒸发式冷风扇|25521|
|daghat.fan.v1ifm|多皓智能风扇|20610|
|dmaker.fan.p23|米家直流变频两季扇|5482|
|ermi.fan.zl2025|yeme电风扇|34220|
|flashm.fan.608|喵动力手持桌面二合一风扇608|39318|
|flashm.fan.f1|喵动力桌面循环扇F-1A|28069|
|flashm.fan.fa9|喵动力壁挂循环扇FA9|38703|
|flashm.fan.s35|喵动力桌面循环扇S35|38704|
|flashm.fan.zl899|喵动力夹式桌面扇ZL899|38597|
|fungu.fan.nkbds1|繁谷多功能吊扇|33780|
|gl2023.fan.6d|Glasslock电风扇|36030|
|gl2023.fan.v1|Glasslock直流变频落地扇|36154|
|gswl.fan.fsx1|HD智能壁挂风扇Z701|26469|
|gswl.fan.v1sfz1|HD智能风扇Z1（BLE）|27306|
|gswl.fan.x1sfb|HD智能风扇X1（BLE）|26080|
|gydzkj.fan.xzfsw|比赛小猪水冷塔扇（WiFi）|34281|
|hcsp.fan.fsns1|奥克斯智能风扇NS-11|36327|
|hcsp.fan.fsns2|奥克斯智能风扇NS-12|36331|
|hcsp.fan.fsns3|奥克斯智能风扇NS-13|36332|
|hcsp.fan.fsns4|奥克斯智能风扇N182|37038|
|hcsp.fan.hsfs|SAPI智能风扇|28368|
|hjhr.fan.hcz11a|皇家惠人10寸折叠伸缩扇HCZ11A|13388|
|hou123.fan.sxdfs|SX-SHUNXIANG循环扇|33503|
|jdjz.fan.2072fc|京东京造空气循环扇XD-2072FC|35067|
|jdjz.fan.35e2r|京东京造电风扇(带驱蚊装置)FS-35E2RY|35697|
|jipin.fan.008|即品智能风循环落地扇|25884|
|jipin.fan.010|即品风随温变智能循环扇|27074|
|jipin.fan.011|即品节能风平面扇|27314|
|jipin.fan.012|即品水冷塔扇|29062|
|jipin.fan.6c|即品一级能效节能直流风扇|35389|
|jipin.fan.f001|即品智能落地风扇|13619|
|jipin.fan.f003|即品智能互联空气循环扇|19155|
|jipin.fan.f004|即品立式空气循环扇|19353|
|jipin.fan.f005|即品空气循环扇|20224|
|jipin.fan.f006|即品智能互联平面落地风扇|20254|
|jipin.fan.f007|即品智能壁挂循环风扇|25034|
|jipin.fan.f008|即品一级能效壁挂风扇|35883|
|jlk.fan.jlkf1|BLEMOFF智能循环扇|35019|
|jmjl.fan.jlpqs|金羚智能夜灯排气扇|29913|
|kadeer.fan.30ar|至凡FS-30ARL风扇|4955|
|kadeer.fan.l15br|至凡FLS-L15BRL无叶冷风扇|4983|
|kadeer.fan.l20xh|至凡FKYT-L20XHDCL落地扇|4982|
|kadeer.fan.ts45hr|至凡FT-TS45HRLDC直流塔扇|4956|
|kaenou.fan.fs05|QYGQ桌面风扇B05|36200|
|kmhb.fan.kmf1|卡曼智能循环电风扇|15321|
|koxi68.fan.892|DS802桌面循环扇|36071|
|koxi68.fan.ds301|DS301桌面循环风扇|36865|
|koxi68.fan.ds803|DS803夹子循环风扇|37589|
|laiex.fan.lesfs|方频智能风扇（BLE）|25463|
|lanbo1.fan.lbfs1|蓝伯摇头桌面循环扇|35805|
|leshow.fan.ss310|乐秀风扇 SS310|1200|
|leshow.fan.ss320|乐秀风扇 SS320|1129|
|leshow.fan.ss4|无叶塔扇|1127|
|miir.fan.ir01|风扇遥控|65721|
|miqu.fan.lmzm2|觅贽桌面折叠扇|36870|
|morlin.fan.dsnfan|帝仕尼智能风扇(WiFi)|26981|
|morlin.fan.ymfan|圆米智能风扇（WiFi）|25409|
|muxnw.fan.m75|慕向引擎循环扇M75|24244|
|nbsxh.fan.alw5dw|苏宁宜品冷风无叶扇( 杀菌加湿版 )|13466|
|nwt.fan.16l|NWT互联网直流变频电风扇|15397|
|nwt.fan.xh001|NWT智能空气循环扇|26598|
|pxiang.fan.2310|苏宁宜品智能循环风扇|14029|
|qjiang.fan.gs02|GS智能风扇J15 Max|26240|
|qjiang.fan.j90|GS智能风扇J90 Max|28475|
|rw02.fan.rw001|RW智能直流变频风扇|35174|
|solove.fan.f5new|素乐智能风扇F5i|1401|
|szxzh.fan.f11|AIVI智能循环扇F11Pro|24466|
|szxzh.fan.f12|KeBinsi智能循环扇F12Pro|25321|
|szxzh.fan.f13|KeBinsi智能循环扇F13Pro|25322|
|szxzh.fan.f1x|KeBinsi 智能循环扇 F1 系|38692|
|szxzh.fan.f23|AIVI智能循环扇 F2 系|27224|
|szxzh.fan.f32|nimin多功能涡轮风扇 F3 系|27221|
|szxzh.fan.f33|AIVI智能循环扇F系|26803|
|szxzh.fan.f52|Hoswn智能循环扇 F52Pro|25704|
|szxzh.fan.f53|AIVI智能循环扇F53Pro|25331|
|szxzh.fan.f55|Hoswn智能循环扇 F55Pro|25300|
|szxzh.fan.f77|AIVI智能循环扇 F7系|31255|
|szxzh.fan.f88|AIVI智能循环扇 F8系|33491|
|szxzh.fan.f99|AIVI智能循环扇 F99Pro|34296|
|tafiq.fan.c1|塔菲克智能风扇|35908|
|tafiq.fan.s26pro|塔菲克智能桌面风扇S26PRO|37333|
|tafiq.fan.s6pro|塔菲克摇头循环风扇S6PRO|36091|
|tms.fan.ftx23a|沙伯AI负离子空气循环扇|25485|
|uvfive.fan.sunny|FIVEHOME智能空气循环扇|11786|
|viomi.fan.v13|云米AI负离子空气循环扇|9151|
|viomi.fan.v5|云米互联网蝶翼仿生电风扇(变频版)|69314|
|viomi.fan.v6|云米互联网空气循环扇|4529|
|viomi.fan.v7|云米互联网直流变频落地扇3|4734|
|wanai.fan.t118|德姆勒电风扇（单冷塔扇）|2648|
|wenxi.fan.yd01|早鱼桌面循环风扇|27248|
|woop12.fan.ldcf|DGUK冰冰空调扇F1|25481|
|xbldqc.fan.s1|XBL-S1壁挂/桌面折叠风扇|30471|
|xfly.fan.d02|小飞吊扇D02|36312|
|xiaomi.fan.p23|米家直流变频两季扇|23697|
|xiaomi.fan.p23w|米家直流变频两季扇|37890|
|xnydz.fan.v1|KFI 智能Ai冷风扇|38294|
|yier.fan.v1|KIMEEY直流变频落地扇|35135|
|yier.fan.v2|KIMEEY直流变频平面扇|35207|
|yier.fan.v3|KIMEEY直流变频循环扇FS1282-DC|35378|
|yier.fan.v4|KIMEEY变频循环扇FS1012R|35428|
|yifang.fan.yx02|一方智能风扇|14258|
|ym001.fan.y1lite|炎米智能手持风扇Lite|38198|
|ym001.fan.ym318|炎米智能手持风扇|35872|
|ym001.fan.ym382|炎米智能便携风扇|35873|
|ym001.fan.ymfs1|炎米智能便携循环扇Y1|37857|
|ym001.fan.ymfs2|炎米智能循环扇Y1|37858|
|ym001.fan.ymfsw|炎米智能风扇（WiFi）|27300|
|yoda.fan.m55|旋风循环扇|14028|
|zh001.fan.zh27|HHGPK智能风扇|36483|
|zh001.fan.zh57|HHGPK智能桌面风扇|36486|
|zh001.fan.zh59|HHGPK桌面循环摇头风扇|37144|
|zhhome.fan.m35|智能吊扇M35|17287|
|zhhome.fan.m55|智能循环扇M55|17343|
|zhhome.fan.m65|智能暴风户外风扇M65|20189|
|zhimi.fan.v2|智米直流变频落地扇|84|
|zw1688.fan.f70|LWU户外风扇|35115|
|zw1688.fan.f80|LWU户外摇头风扇|35537|
|zw1688.fan.lwufs|LWU智能风扇（BLE）|28992|
|zw1688.fan.y08|LWU多功能夹扇Y8|34678|
|zw1688.fan.y12|LWU智能风扇|34382|
|zw1688.fan.y13|LWU智能桌面风扇|35030|
|zyzy1.fan.y07011|智能米家风扇|73540|

## 按 cate_name 的完整缺口

### 个护与起居

|model|name|pd_id|
|---|---|---:|
|090615.curtain.1mcu01|一米未来智能窗帘|68016|
|090615.curtain.a6|帘目A6智能窗帘电机|13974|
|090615.curtain.bofud1|博孚智能卷帘电机|5665|
|090615.curtain.byg247|林氏生活智能窗帘电机|15757|
|090615.curtain.crli82|智能锂电池电机(Mesh)|7724|
|090615.curtain.crus6|平头熊静音窗帘电机(MESH)|15069|
|090615.curtain.curm6|PTX X1隐形窗帘电机|19484|
|090615.curtain.curx1|平头熊 X1超薄隐形电机 Mesh2.0|22088|
|090615.curtain.dj001|花无间DJ-001智能窗帘电机|13972|
|090615.curtain.gr82m1|GR谷雨智能窗帘|12200|
|090615.curtain.h6pro|金蝉智能窗帘电机 H6 Pro|13971|
|090615.curtain.hadj06|皓逸静音窗帘电机(mesh)|13007|
|090615.curtain.jldj03|PTX智能卷帘电机|68023|
|090615.curtain.jxdj02|PTX智能机械卷帘电机|68777|
|090615.curtain.k1pro|平头熊K1 Pro隐藏式窗帘电机|28131|
|090615.curtain.kcz82d|科创者智能窗帘电机|70187|
|090615.curtain.m2|智小金智能窗帘电机M1 (Mesh)|13856|
|090615.curtain.mehe82|咪呵智能窗帘电机|69999|
|090615.curtain.mhl2|平头熊 X1智能梦幻帘电机 Mesh2.0|22929|
|090615.curtain.mia1|米案智能窗帘mesh版|13682|
|090615.curtain.mks6|MEEYA 米亚智能窗帘电机-Ｍ9|13119|
|090615.curtain.mt800w|MEEYA智能窗帘|67175|
|090615.curtain.nmg82|柠檬果智能窗帘电机(WIFI)|73019|
|090615.curtain.osh82d|欧仕恒智能窗帘电机(WIFI)|7461|
|090615.curtain.p01|PTX智能窗帘开关|66696|
|090615.curtain.p1|欧派P1智能窗帘电机|14729|
|090615.curtain.pipacr|噼啪智能窗帘电机|68579|
|090615.curtain.ptcu02|智能语音窗帘电机|8455|
|090615.curtain.ptx82|PTX智能窗帘电机(WIFI)|70134|
|090615.curtain.ptxml1|PTX智能梦幻帘电机|10598|
|090615.curtain.q1pro|平头熊Q1 Pro超薄隐形电机|31108|
|090615.curtain.q6|青菱Q6智能窗帘电机|14730|
|090615.curtain.s2mesh|智能窗帘电机(蓝牙mesh)|6461|
|090615.curtain.s3|三千金S3智能窗帘电机|18251|
|090615.curtain.s6|织选S6智能窗帘电机|15738|
|090615.curtain.s6k1|K1 智能窗帘电机(PTX)|19593|
|090615.curtain.s6min|平头熊S6 mini智能窗帘电机 (Mesh2.0)|27562|
|090615.curtain.s6pro|皓逸智能静音调速电机pro|21732|
|090615.curtain.sidt82|wifi智能窗帘电机|65637|
|090615.curtain.sm82b|苏米智能窗帘电机(MESH)|11338|
|090615.curtain.sumi82|苏米智能窗帘电机|69998|
|090615.curtain.tj01|天居一品TJ-01智能窗帘电机|15758|
|090615.curtain.ws9856|威仕达智能电机|69001|
|090615.curtain.wsdml1|威仕达智能梦幻帘电机|10597|
|090615.curtain.wsjl01|威仕达智能卷帘电机|69016|
|090615.curtain.wtmc01|沃铁隐形窗帘电机|26106|
|090615.curtain.ycur01|YCZNWL 智能窗帘电机|8441|
|090615.curtain.ykgc82|优客工场智能窗帘电机(WIFI)|73018|
|090615.curtain.zs82b|致尚智能窗帘电机(MESH)|11339|
|090615.curtain.zsdj35|致尚智能卷帘电机|69193|
|090615.curtain.zsdj82|致尚智能窗帘电机|69192|
|17216.pillow.pl007|乐伽AI智能颈椎按摩睡眠枕|4084|
|17216.pillow.pl008|乐伽AI智能颈椎按摩睡眠枕|5165|
|25mj.bed.bed001|迈界智能床|28856|
|25mj.sofa.safarm|迈界平推沙发(遥控版)|29446|
|3002.curtain.yjcl1|灵珑窗帘电机（WiFi）|33165|
|3002.curtain.yjcl3|灵珑窗帘电机（Mesh2.0）|38222|
|445.mirror.jg1|大白智联镜柜|31540|
|503923.curtain.sttdt9|斯坦特德窗帘电机 T9|27936|
|666.curtain.em75|A-OK智能窗帘电机|1112|
|666.curtain.gt01|智能窗帘电机|1429|
|666.curtain.gt01m|鲸橙智能窗帘|2304|
|666.curtain.id92|WIFI智能窗帘|2525|
|7499.bed.m2pro|DD智能床M2|36008|
|8278xb.curtain.qwd9|启沃D9智能窗帘|40816|
|888888.curtain.mscl|米舍智能窗帘Mesh2.0|30120|
|abcmk.bed.abcmok|ABCMOKOO智能折叠婴儿床|15458|
|adp.curtain.adbm2|艾达普 卷帘机器人|24005|
|adp.curtain.test02|艾达普 窗帘机器人|18070|
|adp.motor.adfbt6|艾达普 手指机器人(触屏版)|23536|
|adp.motor.adswb4|艾达普 开关机器人|26651|
|adp.motor.f7|艾达普 手指机器人Pro|37782|
|aice.motor.kzmu3|科掌门智能卷帘门控制器|67037|
|aiduo.curtain.adcl02|艾多智能窗帘电机|33850|
|aiduo.curtain.ct05|ID智能窗帘蓝牙Mesh版|22985|
|aikeji.curtain.cura01|AKG智能窗帘电机|38443|
|aise.bed.cds29e|宝褓智能床|39020|
|aixi.curtain.m8pms|艾玺M8PMS智能窗帘Mesh2.0|37791|
|aixi.curtain.m8pro|艾玺M8PM智能窗帘Mesh2.0|37397|
|alight.curtain.cura1|光缓智能窗帘ULTRA|29973|
|amb123.mirror.amb002|欧素智能浴室镜 S1|25005|
|amsi.curtain.yf01|爱漫时隐藏式智能窗帘电机|37899|
|andi.curtain.cura1|ZXWL智能窗帘电机2.0|30067|
|aok98.curtain.am50pw|奥科AM50智能窗帘电机|3956|
|aok98.curtain.aok100|奥科LM100智能窗帘电机|3955|
|aok98.curtain.aok57|奥科AM57开合帘|15988|
|aok98.curtain.aok68|奥科AM68智能窗帘电机|3957|
|aok98.curtain.lm50bw|科创者窗帘电机|9312|
|aok98.curtain.qlam50|青菱Q302智能窗帘|71078|
|aonier.bed.001|澳妮尔智能床|21436|
|artis.sofa.001|Flexnova 智能瑜伽沙发(气囊款)|27962|
|artis.sofa.002|Flexnova 智能瑜伽沙发(基础款)|29266|
|ateai.mosq.dakuo|达阔智能电蚊香|69053|
|atn.curtain.cldjm|ATNSTAR窗帘电机（Mesh2.0）|28700|
|atw.curtain.10mini|AUTORAIL智能窗帘A10mini Mesh2.0|37416|
|atw.curtain.a07|AUTORAIL智能窗帘A07mini Mesh2.0|36861|
|atw.curtain.a10|AUTORAIL智能窗帘A10 Mesh2.0|31446|
|atw.curtain.at5810|AUTORAIL智能窗帘Mesh2.0|29034|
|atw.curtain.at6502|AUTORAIL智能窗帘AT68 Mesh2.0|33317|
|atw.curtain.atw02|AUTORAIL智能窗帘AT06-Mesh2.0|28940|
|atw.curtain.atw07|AUTORAIL智能窗帘A07锂电池版|32140|
|atw.curtain.t01|AUTORAIL智能窗帘T01 Mesh2.0|31447|
|ax01.curtain.cura01|AX-M82G智能窗帘电机|31958|
|ax01.curtain.cura02|AX-M1智能窗帘电机|39795|
|babai.curtain.190812|智能窗帘电机CM(wifi直连)|67505|
|babai.curtain.ad5810|艾德智能窗帘|69861|
|babai.curtain.at5810|奥特威(AUTORAIL)窗帘电机|68196|
|babai.curtain.bb82cb|Ai 智能窗帘（WiFi）|12863|
|babai.curtain.bb82mj|Ai 智能窗帘|68212|
|babai.curtain.bb82mm|Ai 智能窗帘（Mesh）|9249|
|babai.curtain.bjg1|巴百babuy智能卷帘伴侣 G1|31302|
|babai.curtain.bjm1|巴百babuy智能卷帘伴侣 M1|26611|
|babai.curtain.bjw1|巴百babuy智能卷帘伴侣 W1|26690|
|babai.curtain.bjx1|巴百babuy智能卷帘伴侣 X1|24226|
|babai.curtain.ble11s|Ai智能Mesh窗帘|15888|
|babai.curtain.blm1|巴百Mesh窗帘电机 锂电版|37497|
|babai.curtain.bxm1|巴百Mesh窗帘电机Pro|23858|
|babai.curtain.bxw1|巴百WiFi窗帘电机Pro|25973|
|babai.curtain.cm82dm|智能窗帘电机CM|9938|
|babai.curtain.cmb5|CM智能窗帘（WiFi）|16109|
|babai.curtain.cy850|CANY智能窗帘电机|6486|
|babai.curtain.deiyu|兰博尔智能窗帘|17896|
|babai.curtain.jcm3|金蝉M9智能窗帘电机|24146|
|babai.curtain.kyx850|柯雅馨 智能窗帘|4092|
|babai.curtain.lb100a|蓝搏(LANBOO)智能窗帘|69422|
|babai.curtain.lm860|蓝米智能窗帘|7537|
|babai.curtain.ls68m|LS68  Smart Curtain（Mesh）|24869|
|babai.curtain.lsxf83|M3智能窗帘 (WIFI)|18060|
|babai.curtain.m515e|Zemismart 智能窗帘电机|4318|
|babai.curtain.mtx850|满天馨智能窗帘|68399|
|babai.curtain.nh5810|南虎(NanHoo)智能窗帘|68202|
|babai.curtain.osh850|欧仕恒智能窗帘|9074|
|babai.curtain.ql850|LD帘动时代•智慧窗帘|6467|
|babai.curtain.qlm3|青菱Q7mini 智能窗帘电机|23423|
|babai.curtain.xy850|汐研智能窗帘电机|6500|
|babai.curtain.yilc3|小益(Yi-LOCK)智能窗帘 C3|69423|
|babai.curtain.ym25e|禹顺 电动卷帘电机|3941|
|babai.sofa.kh01|金蒂雅居智能沙发|6126|
|babai.wopener.82|辰阳开窗器|10278|
|babai.wopener.83|艾德道开窗器|12640|
|bailer.bed.bed01|追求智能床|37045|
|bayse.motor.m2|bayse卷帘电机控制器M2(Mesh 2.0)|31519|
|bcase.blanket.snt02|向物水暖毯-暖眠眠2|22508|
|bcos.sofa.bcsf02|博畅智能沙发|31306|
|bean.curtain.bct01|智能开合帘电机V1-WiFi版|10092|
|bean.curtain.ct01|智能窗帘电机V1-Mesh版|14020|
|bean.curtain.ct03|森瑞卷帘窗帘电机|16794|
|bean.curtain.ct05|智能窗帘电机S1-Mesh版|19280|
|bean.curtain.ct06|威仕达智能管状窗帘电机-蓝牙Mesh|23027|
|bean.curtain.ct07|威仕达隐藏式开合帘电机|24009|
|bean.curtain.ct23|森瑞日夜帘窗帘电机|19276|
|bean.curtain.ctm1|Ai home窗帘灯带电机|13318|
|bean.curtain.ctw1|威仕达梦幻帘电机-WiFi版|14439|
|bean.curtain.ctw2|科创者智能窗帘电机C5|15002|
|bean.curtain.ctw3|智能开合帘电机V2-WiFi版|15097|
|bean.curtain.ctw6|智能梦幻帘电机A3-WiFi版|17091|
|beb.mattress.byb01|百易宝智能床垫|35823|
|binthe.curtain.bcm|丙申窗帘电动轨道|2039|
|binthe.curtain.bscl|丙申窗帘电机200DE-MH2|27946|
|binthe.curtain.cura02|丙申窗帘电机200D-MH2|26078|
|binthe.curtain.cura03|丙申窗帘电机100DE-MH2|27288|
|binthe.curtain.cura04|丙申窗帘电机20D-MH2|27290|
|binthe.curtain.cura08|丙申智能窗帘电机200DE-MH2|32330|
|binthe.curtain.cura09|丙申智能窗帘电机30D-MH2|33793|
|binthe.curtain.cura10|丙申智能窗帘电机33D-MH2|36882|
|bjkcz.curtain.5max|科创者5Max智能窗帘电机Mesh2.0|32810|
|bjkcz.curtain.kcz05|科创者5Ultra智能窗帘|25540|
|bjkcz.curtain.kcz06|科创者智能窗帘5Ultra-Mesh2.0|25541|
|bjkcz.curtain.kcz09|科创者mini4S智能窗帘Mesh2.0|29581|
|bjkcz.curtain.kcz10|科创者mini4S智能窗帘锂电池版|29582|
|bjkcz.curtain.kcz4|科创者mini4智能窗帘|23532|
|bjkcz.curtain.kczble|科创者mini4智能窗帘Mesh2.0|23533|
|bjkcz.curtain.min5|科创者mini5智能窗帘Mesh2.0|34215|
|bjkcz.curtain.v2|科创者mini4E智能窗帘Mesh2.0|36015|
|bjkcz.curtain.v3|科创者mini4E Pro智能窗帘Mesh2.0|37701|
|bjkcz.curtain.x70|科创者mini5 Pro Max智能窗帘电机|37925|
|bjkcz.motor.kczv2|科创者V1智能窗帘控制器Mesh2.0|40796|
|bjqmzj.curtain.v1|曲美AI智能窗帘电机S7Mesh2.0|39046|
|bjqmzj.curtain.wscmxi|曲美AI智能窗帘电机S5|40653|
|bkrobo.bed.t1|Blupeace 智能助眠床垫|71355|
|bkrobo.bed.t1dbl|Blupeace 智能助眠床垫双人|4800|
|bkrobo.bed.t1sgl|Blupeace 智能助眠床垫单人|4789|
|bkxh.curtain.cura01|小海·见晓开合帘电机标准版|38372|
|bkxh.curtain.cura02|小海·见晓开合帘电机升级版|38373|
|bkxh.curtain.cura03|小海·见晓开合帘电机隐藏版|38374|
|blbm.bed.blbm2|菠萝斑马智能床Max|31559|
|blbm.bed.ele0|菠萝斑马智能床|15222|
|bldjj.sofa.lk001|浪卡智能沙发|32626|
|bnrn.bed.001|浮岛电动床|25090|
|bofu.curtain.82byn|智联82比翼鸟开合帘|15215|
|bofu.curtain.bfmh|梦幻垂直帘|5393|
|bofu.curtain.bfmj|博孚智能开合帘|13127|
|bofu.curtain.ey25|智能卷帘|7226|
|bofu.curtain.normal|智能电动窗帘|5669|
|bofu.curtain.q301|青菱Q301智能窗帘|6655|
|bofu.curtain.sp10xm|世典电动魔幻帘|9777|
|bofu.curtain.zl82xa|蓝牙智能窗帘|10621|
|bogin8.curtain.cura1|柏晶智能窗帘电机|30789|
|boleme.curtain.blmdj|CONTAI 智能窗帘（mesh2.0）|31067|
|boleme.curtain.m98le|CONTAI锂电池智能窗帘|37037|
|boleme.motor.blmdj2|CONTAI智能窗帘C3控制器Mesh2.0|37680|
|brains.curtain.brs001|博瑞思智能窗帘机WIFI版|20510|
|brains.motor.brs001|博瑞思窗帘控制器WIFI版|31738|
|broway.curtain.bem82|博尔美智能窗帘电机|39062|
|btzn.curtain.v1|比特窗帘电机控制器|68849|
|bull.curtain.cl01|公牛窗帘电机CW12|34318|
|bunny.bed.100pro|睡小兔智能床-100pro|37878|
|bw1994.mattress.cnx25|Bestway百适乐安睡智联床垫|30954|
|bymb11.bed.bymb01|柏优美柏智能床|23992|
|bymiot.curtain.m2w|未来居智能窗帘电机M2（WIFI版）|7819|
|bymiot.curtain.mini1|知或居mini智能窗帘Mesh2.0|37405|
|bymiot.curtain.plcv1|未来居PLC智能开合帘电机|81736|
|bymiot.curtain.v2|未来居电动窗帘|67385|
|bymiot.curtain.virv1|未来居通用窗帘电机|75641|
|bymiot.curtain.wlv1|未来居轻连窗帘电机|3585|
|bymiot.curtain.wlv2|未来居无线窗帘电机（M1开合帘）|71764|
|bymiot.curtain.wlv4|未来居智能窗帘电机|20700|
|bymiot.curtain.wlv6|未来居智能窗帘电机(MESH)|21167|
|bymiot.curtain.wlv7|未来居精铸超静音mini窗帘电机2.0|23933|
|bymiot.curtain.wlv9|知或居静音无刷电机mesh2.0|26782|
|bymiot.curtain.yf01|未来居无刷隐藏式窗帘电机|37311|
|caih.blanket.1866|彩虹智能触控电热毯|22437|
|caih.blanket.z1a|彩虹智能触控单人电热毯|37970|
|caih.blanket.z1b|彩虹智能单人电热毯|38244|
|caih.blanket.z2b|彩虹智能双人电热毯|38220|
|calvi.curtain.cam01|CALVI库沃窗帘电机|3549|
|calvi.curtain.kwo01|CALVI窗帘电机-Mesh2.0|35108|
|cchome.curtain.khl01|倍增智能窗帘电机（开合帘）|71666|
|cchome.wopener.tcq001|倍增智能电机控制器|70403|
|cdn.curtain.ct06|西顿开合帘电机K1（隐藏款）|28592|
|cdn.curtain.k1|西顿开合帘电机K1（隐藏款）|39619|
|cdn.curtain.kh01|西顿舍见PLC智能窗帘(开合)|79900|
|cdzkzc.curtain.kh50|智雅悠居智能窗帘电机|25042|
|chens.blanket.001lr|今品森活电热毯|28553|
|chint1.valve.1p|正泰智能控电仪ZTY2001|35027|
|chint1.valve.lcd|正泰智能控电仪ZTY2002|35028|
|chuangmi.curtain.711a02|小白智能窗帘电机 L2|7709|
|chuangmi.curtain.723a02|小白智能窗帘电机 L1C|11311|
|chuangmi.curtain.h209|小白智能窗帘电机蓝牙网关版L1|1960|
|chzn06.blanket.gg001|彩虹乖乖智能水暖毯|21975|
|cmjd.curtain.cm82|XM智能窗帘|9023|
|cmjd.curtain.cm83|智能窗帘|9548|
|cmjd.curtain.cm850|CM智能窗帘-Mesh2.0|28915|
|cmjd.curtain.cm860|CM无刷窗帘电机-Mesh2.0|30613|
|cmjd.curtain.cm88|德裕智能窗帘|11272|
|cmjd.curtain.cmx82|CM电动智能窗帘-Mesh2.0|34183|
|cmjd.curtain.cura1|CM82小精灵窗帘电机|29629|
|coc.dryer.fdpsm|清蜓智能便携干衣机|1515|
|cokit.mosq.coq5|COKIT 智能电热蚊香液加热器CO-Q5|26990|
|cokit.mosq.coq5s|COKIT智能电热蚊香液加热器|28395|
|cokit.mosq.q4p|COKIT智能电蚊香Q4P|35623|
|cokit.mosq.q5p|COKIT智能电蚊香Q5P|35621|
|cooly.sofa.sf001|舒波斐耳智能沙发S1|35234|
|cooly.sofa.sf002|舒波斐耳智能沙发S2|35834|
|cooly.sofa.sf003|舒波斐耳智能沙发S3|35835|
|cqzx.curtain.zxcldj|智信物联窗帘电机Mesh2.0|29499|
|creat6.curtain.ct05|ANKOTTI安科帝窗帘电机|21509|
|czjx.curtain.m3|KERROGAL智能窗帘电机|33532|
|czjx.curtain.m3wifi|KERROGAL智能窗帘电机WiFi|33990|
|czmydz.curtain.myf5|美百帘窗帘主副机(mesh2.0)|39103|
|czmydz.curtain.mym1|美百帘窗帘电机(mesh2.0)|28556|
|czmydz.curtain.myw4|美百帘窗帘电机(WIFI)|34934|
|daolai.motor.jdts|智能激光电视伸缩平台|6804|
|daowei.curtain.cura01|道韦DM82-60智能窗帘电机|35171|
|dayang.mosq.coq4s|COKIT 智能电热蚊香液加热器SE CO-Q4S|25929|
|dayang.mosq.dyt16s|俏蜻蜓灭蚊灯|2893|
|dayang.mosq.qqtm6|俏蜻蜓智能灭蚊灯PRO QQT-M6|12255|
|dayang.mosq.qqtq4|COKIT 智能电热蚊香液加热器CO-Q4|12256|
|deruci.bed.mcw1|慕思智能空气垫Air-pro|4902|
|dfwlw.curtain.sttdst|斯坦特德窗帘电机ST9|26097|
|dfwlw.motor.xy02kg|希崖门控|21865|
|difeis.curtain.d1|帝菲斯智能窗帘D1|71300|
|dlsp.sofa.sf001|梦汀美智能沙发|33225|
|dlsp.sofa.sf002|德联尚品智能沙发|33408|
|dlsp.sofa.sf003|酷晵智能沙发|33409|
|dlx.curtain.cl11|德力西电气窗帘电机|26413|
|dlx.curtain.cura01|德力西电气隐藏式窗帘电机|38727|
|dmlink.bed.z7s|SmartZZ智能床|30977|
|dnake.curtain.ct05|狄耐克智能窗帘电机S1-Mesh版|21472|
|dnake.curtain.d82|狄耐克智能窗帘电机（Mesh2.0）|37531|
|dnake.curtain.mini|狄耐克智能窗帘电机Mini（Mesh2.0）|37530|
|doco.fcb.docov001|DOCO 微电流精华导入美容仪|1266|
|doorma.curtain.cura01|Ai home智能窗帘Mesh版|15936|
|doorma.curtain.cura02|DM智能窗帘电机|26756|
|doorma.curtain.dmcl|科思顿X6无刷电机|28640|
|doorma.curtain.dmjldj|DMA智能卷帘电机（Mesh2.0）|30213|
|doorma.curtain.ksdcl|科思顿智能窗帘|23954|
|doorma.curtain.v3cl|科思顿智能窗帘X6|27309|
|doorma.curtain.v3cld8|科思顿智能窗帘D8|27308|
|dooya.curtain.230x5|杜亚智能窗帘X5|14569|
|dooya.curtain.270q5|杜亚智能窗帘Q5|15494|
|dooya.curtain.998tm|杜亚智能窗帘DT998TM|30217|
|dooya.curtain.99tn|杜亚智能窗帘D12|17480|
|dooya.curtain.a8|杜亚智能窗帘A8|28943|
|dooya.curtain.c1|杜亚智能卷帘控制器 C1|70321|
|dooya.curtain.d10x|杜亚智能窗帘D10|19890|
|dooya.curtain.d11x|杜亚智能窗帘D11|19690|
|dooya.curtain.d15x|杜亚智能窗帘D15|19683|
|dooya.curtain.d1li|杜亚智能窗帘M7Li|16714|
|dooya.curtain.d1xc|杜亚智能窗帘D1-XC|8029|
|dooya.curtain.d21|杜亚智能窗帘D21|22943|
|dooya.curtain.d22|杜亚智能窗帘D22|22944|
|dooya.curtain.d25p|杜亚智能窗帘K7-X|35997|
|dooya.curtain.d3|杜亚窗帘宝D3|17200|
|dooya.curtain.d3pro|杜亚智能窗帘宝D3|24231|
|dooya.curtain.d8|杜亚智能窗帘D8-BM|24027|
|dooya.curtain.d8xc2|杜亚智能窗帘D8-XC|15967|
|dooya.curtain.d8xwb|杜亚智能窗帘D8-XWB|5106|
|dooya.curtain.d97|杜亚智能窗帘DT97|31865|
|dooya.curtain.d9pro|杜亚智能窗帘D9|17745|
|dooya.curtain.db8bm|杜亚智能窗帘DB8 BM|37466|
|dooya.curtain.dk66|杜亚智能梦幻帘MH8|17118|
|dooya.curtain.dk71|杜亚智能梦幻帘DK70|19370|
|dooya.curtain.dk80|杜亚智能梦幻帘电机DK80|24469|
|dooya.curtain.dt100t|杜亚智能窗帘DT100TM|32397|
|dooya.curtain.dt230|杜亚智能窗帘DT230|20159|
|dooya.curtain.dt79lx|杜亚智能窗帘DT79FH/BM|35036|
|dooya.curtain.dt79s|杜亚智能窗帘DT79FM/BM|35029|
|dooya.curtain.dt82n|杜亚智能窗帘DT82|18002|
|dooya.curtain.dt860|杜亚麒麟智能窗帘860|13006|
|dooya.curtain.dt92|杜亚智能窗帘DT92|19691|
|dooya.curtain.dt95a|杜亚智能窗帘氛围大师D23|25691|
|dooya.curtain.dt97|杜亚智能窗帘JC系列S7|29443|
|dooya.curtain.dt98|杜亚智能窗帘DT98|23564|
|dooya.curtain.dt9897|杜亚隐藏款智能窗帘|38916|
|dooya.curtain.dt98lx|杜亚智能窗帘DT98LX|27559|
|dooya.curtain.dt98tm|杜亚智能窗帘real 5|23660|
|dooya.curtain.dt99tm|杜亚智能窗帘DT99TM|24928|
|dooya.curtain.duals|杜亚分控智能窗帘|38723|
|dooya.curtain.dy3|杜亚智能窗帘DY3|23330|
|dooya.curtain.fc3|杜亚智能日夜蜂巢帘控制器FC3|35941|
|dooya.curtain.fc4|杜亚智能日夜蜂巢帘控制器FC4|34359|
|dooya.curtain.fct9|杜亚智能窗帘 翡翠T9|37842|
|dooya.curtain.flex25|杜亚左右分控开合窗帘D25|25281|
|dooya.curtain.h98|杜亚智能窗帘H98|31444|
|dooya.curtain.k10x|杜亚智能窗帘K10-X|35999|
|dooya.curtain.k12pro|杜亚智能梦幻帘K12-X|23350|
|dooya.curtain.k5x|杜亚智能窗帘K5-X|38563|
|dooya.curtain.k60|杜亚智能梦幻帘DK60|12775|
|dooya.curtain.k8|杜亚智能窗帘K8 Pro|30781|
|dooya.curtain.kk6x|杜亚智能窗帘 K6-X|35303|
|dooya.curtain.km2|向日葵智能窗帘KM2-C|21118|
|dooya.curtain.m03|杜亚智能窗帘M3|7381|
|dooya.curtain.m1|杜亚智能窗帘m1|67461|
|dooya.curtain.m11|杜亚智能窗帘M11|16606|
|dooya.curtain.m11mn|杜亚智能窗帘M11 mini|24398|
|dooya.curtain.m12|杜亚智能窗帘M12|22297|
|dooya.curtain.m18|杜亚智能窗帘M18|24040|
|dooya.curtain.m1p|杜亚智能窗帘M1|18270|
|dooya.curtain.m1wf|杜亚智能窗帘m1 WF|32219|
|dooya.curtain.m2|杜亚智能窗帘m2|70652|
|dooya.curtain.m2p|杜亚智能窗帘M2|17976|
|dooya.curtain.m2pro2|杜亚智能窗帘m2 TER|27117|
|dooya.curtain.m2te|杜亚智能窗帘m2 WF|31721|
|dooya.curtain.m5|杜亚智能窗帘|68700|
|dooya.curtain.m5wf|杜亚智能窗帘m5 WF|32220|
|dooya.curtain.m7|杜亚智能窗帘M7|7953|
|dooya.curtain.m7li|杜亚智能窗帘M6Li|11866|
|dooya.curtain.m7p|杜亚智能窗帘m7Pro|24534|
|dooya.curtain.m9pro|杜亚智能窗帘M9|22994|
|dooya.curtain.mc3|杜亚智能窗帘控制器C5|34325|
|dooya.curtain.mc5|杜亚智能窗帘MC5|20357|
|dooya.curtain.mc5pro|杜亚智能窗帘MC5PLUS|20697|
|dooya.curtain.mc9fm|杜亚智能窗帘氛围大师MC9 FM|37236|
|dooya.curtain.mcc5|杜亚智能窗帘Mc5|32221|
|dooya.curtain.mh9|杜亚智能梦幻帘MH9|21690|
|dooya.curtain.r5p|杜亚智能窗帘Real5 Pro|35044|
|dooya.curtain.r6ph|杜亚智能窗帘REAL6 PRO|37980|
|dooya.curtain.r6plx|杜亚智能窗帘Real6 Pro LX|35043|
|dooya.curtain.r8762e|向日葵智能窗帘KM2|20421|
|dooya.curtain.real6|杜亚智能窗帘Real 6|30463|
|dooya.curtain.real6p|杜亚智能窗帘Real6 Pro|33449|
|dooya.curtain.rjp200|杜亚智能窗帘 锐界P200|37720|
|dooya.curtain.s2m|向日葵智能窗帘S2M|23184|
|dooya.curtain.s3m|向日葵智能窗帘S3M|23563|
|dooya.curtain.s90|杜亚智能窗帘S90|32402|
|dooya.curtain.tslx|杜亚智能窗帘TSL X|35276|
|dooya.curtain.w1578|DT82TN/S|69484|
|dooya.curtain.x7|杜亚智能窗帘X7|14600|
|dooya.curtain.x7mesh|杜亚智能窗帘X7 mesh|22814|
|dooya.curtain.x7pro|杜亚智能窗帘X7Pro|15227|
|dooya.curtain.x9|杜亚智能窗帘X9|18770|
|dooya.curtain.ys7|杜亚智能窗帘Real 5|19995|
|dooya.curtain.z7mesh|杜亚智能窗帘Z7|19099|
|dooya.curtain.z82|帘邦印象智能窗帘Z8WIFI|17544|
|dooya.curtain.z8mesh|帘邦印象智能窗帘Z8|18692|
|dooya.motor.1545mc|杜亚智能窗帘控制器C3|30198|
|dooya.motor.ck1|杜亚成品帘控制器|22347|
|dooya.motor.dc1545|杜亚智能卷帘控制器 WF|31480|
|dooya.motor.lidian|杜亚智能成品帘控制器-锂电池版|21715|
|dooya.motor.pfc|杜亚智能屏风帘控制器|31936|
|dooya.motor.riye|杜亚智能日夜蜂巢帘控制器FC2|21531|
|dooya.wopener.8807h0|杜亚智能开窗控制器DC8807H|27138|
|dotop.curtain.82|大道梦想家 智能窗帘|11492|
|dpstar.motor.busmot|典派巴士门电机|25578|
|dpstar.motor.panmot|典派平移电机|25577|
|dpstar.motor.unimot|典派电机控制器V1|25579|
|dreame.curtain.a1|追觅智能窗帘电机A1 Ultra|37260|
|dreame.curtain.a1pro|追觅智能窗帘电机A1 Pro|33528|
|dreame.curtain.d01w|追觅智能窗帘电机|29699|
|dreame.curtain.m1|追觅智能窗帘电机M1|33529|
|dxxq.bed.yu7|大象星球智能床 M1|37885|
|dzdq.blanket.denc01|Denc帝仕尼温泉仓水暖毯|23800|
|eairpo.bed.mi12|爱璐仕新风控温床垫|7322|
|ecof1.curtain.ykcl|易可纺智能窗帘(Mesh2.0)|27146|
|egch.curtain.ftcl1|元雁智能窗帘（Mesh）|30934|
|eizi.toothbrush.sy01|EIZI亦己超净AI智能牙刷MAGIC 01|10788|
|enchen.razor.bs8|映趣智能剃须刀BS8|16314|
|enchen.razor.d8|映趣智能剃须刀D8|18364|
|enchen.razor.z4|映趣智能剃须刀K8 Plus|21734|
|enjia1.bed.ej001|恩嘉智能床|6586|
|enjia1.sofa.ej002|恩嘉智能沙发|6612|
|enwo.bed.ec302|宝格梦一体智能床|32868|
|enwo.bed.ec304|宝格梦分区智能床|32869|
|ermi.blanket.snt01|yeme智能水暖毯|30892|
|ermi.blanket.zeemi1|yeme智能除螨电热毯（单控）|30560|
|ermi.blanket.zeemi2|yeme智能除螨电热毯（双控）|30561|
|evecca.wopener.bwn4py|易慧家内开开窗器4 Pro|34270|
|evecca.wopener.bwp03|易慧家智能推拉开窗器1C|13002|
|evecca.wopener.bwp4py|易慧家平开开窗器4 Pro|33849|
|evecca.wopener.na03ma|易慧家联网助手3|18231|
|f123.curtain.f3|帘玺智能窗帘电机 F2|37941|
|f123.curtain.m2|帘玺智能窗帘电机 M1|37948|
|feid.curtain.ct|飞雕薄静智能窗帘电机|39222|
|feiyu.hair.am02|KiCA高速无线吹风机|13425|
|fenjun.mosq.m1pro|懒小兽 电热驱蚊器 U4 Pro|36305|
|fgj.bed.rcctgc|智能床头柜|4667|
|fiser.valve.bhq2p|浦安达单相智能通断器Pro|27666|
|fr1698.mattress.atbb50|睡丽派智能宝宝舱|21429|
|fr1698.mattress.atm180|睡丽派智能床垫|21399|
|fssmk.blanket.dk01|Haotaitai智能水暖毯|29851|
|fssmk.blanket.sk01|Haotaitai智能双控电热毯|29852|
|fssmk.blanket.sndrt|Haotaitai智能电热毯|32872|
|ftd.curtain.wibyil|FTD智能窗帘电机V1(MESH)|20466|
|galime.curtain.gm46|叮咚智能开合帘|6122|
|galime.curtain.gp72|叮咚智能平移式开窗器|6111|
|galime.curtain.gz45|叮咚智能卷帘电机|6110|
|galime.curtain.lime01|GALIME智能窗帘Mesh2.0|29126|
|galime.curtain.lime02|GLMD锂电池智能窗帘|29127|
|gamder.curtain.jdkhl|家的智能窗帘电机|37776|
|gamder.curtain.jdkhl2|雅点智能窗帘电机|38232|
|gaodi.sofa.001s|卡萨驰智能电动沙发SFY004|17202|
|gaodi.sofa.002t|卡萨驰智能电动沙发Z003|17203|
|gaosd.curtain.cmotor|高事达PLC窗帘电机_MICMK-01|79997|
|gayoo.curtain.gyclg1|光言光语 静音开合窗帘Mesh2.0|29860|
|gdxdkj.blanket.01|小达智能水暖毯|6814|
|gdxdkj.blanket.smxdr1|小达石墨烯智能低压电热毯|74260|
|gdxdkj.blanket.znsnt|小达静音智能水暖床垫|11093|
|gee1.wopener.c02b|Geesmart 智能开窗器C02|22306|
|geiger.curtain.ftzndj|GEIGER 智能窗帘电机(Mesh2.0)|31153|
|gerwin.curtain.25xm|GM智能电动窗帘xm|20336|
|gerwin.curtain.gm24tf|GM日夜帘电机|16948|
|gerwin.curtain.gm25l|GM智能电动窗帘|14021|
|gerwin.curtain.gm25xm|GM智能窗帘|4148|
|gerwin.curtain.gm35xm|GM智能窗帘电机|6595|
|gerwin.curtain.zldj|GM智能开合帘（Mesh2.0）|27744|
|gerwin.curtain.zljldj|GM智能卷帘（Mesh2.0）|30164|
|getuo1.wopener.znmc|GAPOSA智能开窗器|32758|
|giot.curtain.v1icm|V1智能窗帘（Mesh）|15341|
|giot.curtain.v2bsm|V2Gra锂电池卷帘（Mesh）|23413|
|giot.curtain.v5icm|V1锂电池智能窗帘（Mesh）|13804|
|giot.dryer.v1icd|V1Gra智能干衣机|21784|
|giot.motor.v1imm|V1电机控制器（WiFi）|18794|
|giot.valve.valve1|Gosvn高山领航智能阀门控制器蓝牙MESH版|18687|
|giot.wopener.v1iwom|Gra电动控制器V1（Mesh）|20026|
|gmrii.curtain.gt30|格米力智能窗帘GT30TV/P|4368|
|gmrii.curtain.gt50|格米力智能窗帘GT50TV/M|4714|
|googo.curtain.cura01|mitch智能窗帘电机|27736|
|gswl.curtain.v3cl|HD窗帘电机X3（Mesh2.0）|26379|
|gszn.motor.gs168|国顺通用控制器|11270|
|gt1688.curtain.sw001|自然爱窗帘电机Q1 Mesh2.0|27216|
|guchi.bed.zn|谷驰智能床|35609|
|gudi.curtain.cura01|固帝智能Mini窗帘电机|33606|
|gujia.sofa.a01|顾家智能沙发A01|26751|
|guoshi.other.sem01|Hi+智能蒸汽眼罩|1290|
|guoskj.sofa.sofa01|法莎蒂智能沙发|26312|
|guznos.curtain.gzcldj|光正智能窗帘|33715|
|gxdz.curtain.dg168|单轨一体化电动窗帘|6195|
|gxdz.curtain.gx168|双轨一体化电动窗帘|5449|
|gyzn.curtain.ct01|光韵MINI智能窗帘电机|30772|
|gyzn.curtain.ct02|光韵双擎智能窗帘电机|34854|
|gyzn.curtain.ct05|光韵智能氛围灯窗帘电机|22164|
|gyzn.curtain.ct07|光韵智能氛围灯卷帘窗帘电机|26722|
|gzkj.curtain.cura01|GZ智能窗帘mesh2.0|34202|
|gzzn.curtain.cura01|ANTJIUJIU 智能窗帘电机|31563|
|haier.curtain.ct05|Haier隐藏式智能窗帘电机HPM-13Y1Q-UD|22091|
|haier.curtain.cura01|海尔智能窗帘电机|19190|
|haoyi.curtain.hyclv3|皓逸mini窗帘电机Mesh2.0|32170|
|haoyi.curtain.minip|皓逸MiNi窗帘电机Pro|40575|
|hbzd88.blanket.hddrt|环岛智能电热毯|31000|
|hddz.blanket.zndrt|智能电热毯|67822|
|hdm111.bed.hdm001|HDM电动床HDM-D3|24724|
|hetmod.pillow.snore|云触智能舒鼾枕M1|24904|
|hjhr.blanket.hrs51|皇家惠人智能水暖毯SH2-SN04|16733|
|hlznkj.dental.cs60a|奈帕智能电动冲牙器CS60A|13347|
|hlznkj.toothbrush.se40a|奈帕智能便携声波电动牙刷|13359|
|hmd.bed.001|好梦得0压智慧床|25495|
|hnjc.hair.s01|早鱼高速吹风机|24549|
|homray.sofa.zhsm1|芝华仕智能沙发M1|12846|
|honyar.curtain.ct01|鸿雁智能窗帘电机V1|32401|
|honyar.curtain.cura01|鸿雁智能窗帘HM|24762|
|honyar.curtain.cura02|鸿雁智能窗帘电机HM2.0|26273|
|honyar.curtain.cura05|鸿雁隐藏式智能窗帘电机|34139|
|hopo.wopener.hb01|HOPO 平开窗开窗器|30286|
|hopo.wopener.pk901|HOPO平开窗开窗器PK901|39325|
|horow.mirror.a70m02|希箭IOT智能镜柜a70m02|14333|
|horow.mirror.a80m02|希箭IOT智能镜柜a80m02|14334|
|horow.mirror.b55m02|希箭IOT智能镜柜|12826|
|horow.mirror.b75m02|希箭IOT智能镜柜b75m02|14330|
|horow.mirror.b85m02|希箭IOT智能镜柜b85m02|14331|
|horow.mirror.b95m02|希箭IOT智能镜柜b95m02|14332|
|hr2025.curtain.hr01|HR智能窗帘Mesh2.0|29236|
|hr2025.curtain.hr02|HR智能隐形分控窗帘|36680|
|hszn.curtain.hscl|华时智能窗帘电机（Mesh2.0）|28070|
|htwl.dryer.v1|洪塔智能烘鞋机|2264|
|huachu.dryer.xqd100|小器点智能衣护宝|2067|
|huadn.blanket.001|HUADN智能数显电热毯|20536|
|huadn.blanket.002s|HUADN智能单控数显电热毯|27302|
|huadn.blanket.003|HUADN智能发热垫|28472|
|huadn.blanket.123456|环鼎水暖毯|5856|
|huadn.blanket.abcdef|GIPIN水暖毯|7776|
|huadn.blanket.hd|环鼎智能水暖毯HD|19296|
|huadn.blanket.hd001|环鼎智能恒温水暖毯|25636|
|huadn.blanket.hd002|环鼎智能双控水暖毯|31349|
|huadn.blanket.hd004|环鼎智能双控电热毯|39518|
|huafu.curtain.cura01|桦府智能窗帘电机N2|34144|
|huhu.blanket.001|绒王防爆缸水暖毯R7|29865|
|hxiao.curtain.cur01|皆美智能窗帘JML2|29762|
|hxiao.curtain.jm68|皆美智能窗帘JML1|30605|
|hxiao.curtain.jmm3|皆美智能窗帘JMS1|30604|
|hxiao.curtain.mjs2|皆美智能窗帘JMS2|30290|
|hzym88.mosq.pd02|臻邦 X10 Ultra AI智能灭蚊器|27236|
|hzyx01.beauty.m180|语爱美智能全效射频美容仪M180|13253|
|hzzl.curtain.zm3|众帘ZM3智能窗帘电机|35589|
|iot.bed.ddc01|喜临门智慧T1智能床|22232|
|iot.bed.upone|蓝盒子电动床|19573|
|iot.curtain.cldj|奥科AM卷帘电机|21989|
|iotpfk.valve.003|iotperfect阀门智能控制器（Mesh2.0）|31275|
|isleep.blanket.hs2001|绘睡一键舒眠水暖垫HS2001|3146|
|isleep.blanket.hs2201|绘睡一键舒眠水暖垫HS2201|5451|
|isleep.blanket.hs2205|绘睡水暖垫HS2205|5452|
|isleep.blanket.hs2401|绘睡水暖垫HSWS-1|21061|
|jbl123.curtain.cura01|金百丽智能窗帘|25376|
|jdjz.bed.001|京东京造百变大师智能床JZ002-S|30039|
|jdjz.bed.002|京东京造百变大师智能床JZ003-S|30040|
|jdjz.bed.xmx|京东京造 X EasyZzz JZ005智能床|33098|
|jipin.blanket.002|即品智能可水洗电热毯|22173|
|jipin.blanket.005|即品碳晶电热地垫|25853|
|jipin.blanket.cmsnt|即品智能互联水暖毯|32274|
|jipin.blanket.cwt602|即品智能宠物毯|38733|
|jipin.blanket.snt1|即品智能恒温水暖毯|30314|
|jipin.blanket.snt1sk|即品智能双控双区水暖毯|30443|
|jipin.blanket.tt7xxa|即品智能除螨电热毯|9509|
|jipin.blanket.ttdk|即品智能互联单控电热毯|31637|
|jipin.blanket.ttsk|即品智能互联双控电热毯|31636|
|jmzc.curtain.zcr01|哲成智能窗帘电机|30201|
|joony.bed.jn002|JOONY佐尼智能床|37652|
|joony.bed.jn004|JOONY佐尼分体智能床|37653|
|jrj.toothbrush.j3m800|杰瑞佳 imoya 智能电动牙刷|12840|
|jsa.valve.jsa|居水安智能水浸阀|36095|
|jsjj.bed.j01|法兰琳卡智能床|23437|
|jstar.curtain.jcd25|JC智能卷帘电机|8847|
|jstar.curtain.jcn24|JC卷帘电机|13984|
|jstar.curtain.jcn30|JC智能窗帘|29526|
|jstar.curtain.jcv24|JC智能百叶帘电机|8846|
|jstar.curtain.stew|JC智能窗帘电机|4852|
|jtjiot.curtain.2ecbl|捷特佳双驱无刷窗帘电机2EC-BL|39936|
|jtjiot.curtain.cura01|捷特佳无刷窗帘电机|39931|
|junpai.curtain.ct01|骏派小金刚氛围灯窗帘电机MESH|30775|
|junpai.curtain.jp601|JP601小金刚mini窗帘电机|39361|
|junpai.curtain.jp68|JP700大力士窗帘电机|40556|
|junpai.curtain.m3|JP500小财神智能窗帘电机|39360|
|juyou.bed.h7|居优智能电动床|27071|
|jwzn.curtain.cura1|佳文智能窗帘电机E7|29681|
|jxatm.bed.hhks01|花花卡莎智能床|26179|
|jytzn.bed.jyt|CX智能电动床|27500|
|k0918.toothbrush.kid01|贝医生儿童声波电动牙刷（智能故事版）|1441|
|kaenou.mosq.v1|QYGQ智能电热驱蚊器|35206|
|kairu.blanket.nrdrt|三顺暖润智能电热毯(WiFi)|32778|
|kavtr.sofa.ysbn1|宜世布诺智能沙发|25726|
|kbs001.curtain.kbsdj|科博士窗帘电机|33504|
|keeson.bed.sfd001|舒福德智能床S4161D|27766|
|keey.curtain.qyclm|KEEY智能窗帘（Mesh2.0）|28891|
|keey.curtain.qyclm1|KEEY 智能梦幻帘电机|34058|
|keey.curtain.qyclm2|KEEY 智能无刷窗帘电机|37324|
|keey.curtain.qyjlm|KEEY 智能管状窗帘电机|34313|
|keey.curtain.qyjlm2|KEEY 智能日夜蜂巢帘窗帘电机|34973|
|keey.curtain.qyjlm3|KEEY 智能管状窗帘电机-Turbo|38350|
|khznkj.razor.ks8521|智能剃须刀|14952|
|klf.bed.m100|卡路福语音控制智能电动床波尔克|38933|
|klf888.curtain.cura01|客来福智能开合帘电动窗帘|20870|
|kmt.curtain.kmtk1|KOMACHT智慧Ai窗帘电机|35698|
|kola.milk.v1|考拉妈妈智能控温冲奶机|483|
|krst.bed.001|舒诗梦智能床|27502|
|ksc.curtain.px1|金云智联窗帘电机X1（PLC版）|80923|
|ksks.curtain.cura01|今上智能窗帘Pro|27988|
|ktkj.wopener.kcwv01|康拓智能开窗控制器|9791|
|kuka.bed.m|顾家智能床|40091|
|kuxi.curtain.curt02|酷犀无刷隐藏电机|33556|
|kyok.curtain.kycl|科译窗帘电机（Mesh2.0）|31618|
|kyoung.blanket.area2|彩阳石墨烯水洗电热毯（两温区）|30318|
|kyoung.blanket.area4|彩阳石墨烯水洗电热毯（四温区）|28962|
|lanju.mosq.mosq1|榄菊智能电热蚊香液加热器Y1|37852|
|lat888.curtain.ct66|迅为智能窗帘电机Mesh2.0|26407|
|lbhd.razor.hs150|电动剃须刀|12488|
|ldzn.curtain.cura01|凌动智能 开合帘电机2.0|26846|
|ldzn.curtain.cura2|凌动智能 Mini窗帘电机2.0|30068|
|ledmy.curtain.cura01|乐的美智能窗帘|38764|
|leike.curtain.cura01|雷克智能窗帘|37410|
|lemesh.curtain.cura01|情景mesh窗帘电机|7222|
|lemesh.curtain.cura02|情景开合电机WIFI S2版|11426|
|lemesh.curtain.cura07|情景Lemesh窗帘电机11S版|22558|
|lemesh.curtain.cura08|情景Lemesh窗帘电机Ultra|23266|
|lemesh.curtain.curb02|情景Mesh卷帘V2|14407|
|lemesh.curtain.curh01|HT智能窗帘电机(Mesh版)|12807|
|lemo.bed.bedjd3|lemonai柠檬智能床|34734|
|leshi.curtain.v0001|情景开合电机WIFI X版|1471|
|lex.curtain.cura01|LEXMesh 智能窗帘电机2.0|24418|
|lf1955.bed.001|龙凤家居智能床|29036|
|lhz.curtain.cura01|罗格朗迷你窗帘电机|35128|
|lhz.curtain.motor1|罗格朗智能窗帘电机MESH版|21310|
|line.bed.bed01|志邦智能床|27900|
|line.curtain.8m1|LineHope智能窗帘电机8M1|5457|
|line.curtain.azm01|Azena智能窗帘电机|6897|
|line.curtain.cldjr1|LineHope智能窗帘电机R1|11021|
|line.curtain.cldjr6|LineHope智能窗帘电机R6|23351|
|line.curtain.dm1|LineHope智能窗帘电机DM1|5074|
|line.curtain.fdjr1|方舟鱼智能窗帘电机R1|14684|
|line.motor.t8|TATACASA智能滑轨电机控制器TL001|20876|
|lingte.motor.ltg008|达睿特卷帘门电机控制器|26790|
|lingte.motor.ltg011|达睿特管状电机控制器|30069|
|lingte.motor.ltg012|达睿特全频拷贝电机控制器|35364|
|linju.motor.ljkzq|聆巨智能电机控制器|35777|
|linju.valve.sw0a03|聆巨机械手阀门控制器(Mesh)|23371|
|linp.curtain.c2|领普窗帘电机MESH|10807|
|linp.curtain.c3|智能窗帘电机C3（PLC版）|77278|
|linp.curtain.c4b|领普智能窗帘电机C4|16120|
|linp.curtain.c5db|领普智能窗帘电机（Mesh2.0）|24927|
|linp.curtain.c6db|领普隐藏式窗帘电机C6|33393|
|linp.curtain.ec1db|领普隐藏式窗帘电机|28968|
|linp.curtain.lpc1|领普窗帘电机|3798|
|linp.curtain.t2db|领普隐藏式窗帘电机T2|35744|
|linp.wopener.wd1lb|领普智能平移推窗器WD1|10939|
|linp.wopener.wd2lb|领普智能平开推窗器WD2|13203|
|liyan.wopener.liyan|亮庭开窗器|29288|
|ljzp.curtain.khldj|俪居外星来客窗帘|19231|
|ljzp.curtain.ljxhg|俪居小黑管窗帘|19558|
|lk07.curtain.cura1|lanke智能窗帘电机(MESH)|32409|
|lkzm.curtain.cura01|雷卡之星智能电动窗帘2.0|33489|
|lmdsz.blanket.blkt01|LMDMAKE深睡智眠电热毯|30641|
|lmier.blanket.lfdrt|朗妃智能电热毯(WiFi)|31377|
|lnjj.bed.001|良年电动床2D|30043|
|lnjj.bed.002|良年电动床4D|30045|
|longs.curtain.lscm02|龙胜智能窗帘电机|33554|
|lonsam.curtain.001|LS智能窗帘电机|7200|
|lonsam.curtain.123|LS M3电动窗帘(Mesh)|5755|
|lonsam.curtain.68ur|LS Mesh2.0智能窗帘电机68|30458|
|lonsam.curtain.82c|LS 智能窗帘电机M82C(mesh2.0）|37316|
|lonsam.curtain.82wif|LS WiFi智能窗帘电机82|30423|
|lonsam.curtain.ct05|LS-M3 CURTAIN-Mesh|21066|
|lonsam.curtain.ct05a|LS SMART CURTAIN|21749|
|lonsam.curtain.ct06|LS mini curtain motor|23687|
|lonsam.curtain.ct06a|LS SMART CURTAIN Mesh 2.0|23688|
|lonsam.curtain.lm25a|LS智能卷帘(WiFi)|22701|
|lonsam.curtain.lm25am|LS智能卷帘(Mesh)|22699|
|lonsam.curtain.ls99mb|LS Mesh2.0智能窗帘电机99-Y|30519|
|lonsam.curtain.lscl|LS智能窗帘|5195|
|lonsam.curtain.lsm01|LS Smart Curtain （mesh2.0）|28500|
|lonsam.curtain.lsm02|LS Mesh2.0智能窗帘电机 82|31228|
|lonsam.curtain.lsm99|LS智能窗帘电机M99|39499|
|lonsam.curtain.lsv3|LS智能窗帘电机（mesh2.0）|28355|
|lonsam.curtain.m100|朗森M100智能窗帘电机|37323|
|lonsam.curtain.m3lim1|LS 锂电池窗帘电机M3Li|32424|
|lonsam.curtain.m3soc|LS Smart Curtain|28551|
|lonsam.curtain.m3wii|LS WiFi智能窗帘电机M3|31965|
|lonsam.curtain.m5foc|LS Mesh2.0无刷智能窗帘电机B2-B|29326|
|lonsam.curtain.m5wif|LS WiFi无刷智能窗帘电机B2-B|30418|
|lonsam.curtain.m6ur|LS Mesh2.0智能窗帘电机M6|30358|
|lonsam.curtain.m8|LS M8智能窗帘电机mesh2.0|38366|
|lonsam.curtain.m82gmb|LS Mesh2.0智能窗帘电机M82GS|31388|
|lufu.bed.lufu01|路福智能床M9|23318|
|lufu.bed.lufu02|路福智能床|34174|
|lumi.curtain.acn002|Aqara智能卷帘伴侣 E1|72011|
|lumi.curtain.acn006|米家智能窗帘 锂电池版|4722|
|lumi.curtain.acn014|Aqara智能窗帘电机 E1|9964|
|lumi.curtain.aq2|Aqara智能管状电机|568|
|lumi.curtain.hagl04|Aqara智能窗帘电机 B1|66336|
|lumi.curtain.hagl05|小米有品智能窗帘电机（Wi-Fi版）|1268|
|lumi.curtain.hagl08|Aqara智能窗帘电机 A1|2662|
|lumi.curtain.hmcn01|米家智能窗帘|2115|
|lumi.curtain.hmcn02|米家窗帘伴侣|3129|
|lumi.curtain.hmcn04|米家窗帘伴侣组|71017|
|lumi.curtain.mcn005|米家智能窗帘1S|7652|
|lumi.curtain.v1|Aqara智能窗帘电机（Zigbee开合帘版）|163|
|luoban.curtain.cura01|LB智能窗帘Mesh2.0版|34884|
|lvgmbh.curtain.ldwscl|朗德万斯智能窗帘电机|39930|
|lxun.curtain.cl01|智能窗帘电机mesh版|12118|
|lxzn.valve.02|LTP智能导轨式断路器1P-MESH|21562|
|lzmesh.curtain.cura01|朗尊 MESH2.0 迷你型智能窗帘电机|27982|
|lzmesh.curtain.cura02|朗尊 MESH2.0 82型智能窗帘电机|27983|
|mcosu.curtain.pipae1|F1 MESH电机|12036|
|meio.blanket.kmdrt|酷盟智能电热毯(WiFi)|31727|
|menred.valve.v8hsm|曼瑞德智能阀门（Mesh2.0）|28169|
|miaomiaoce.blanket.d02|PMA-秒秒测智能低压电热毯（双人）|67374|
|miaomiaoce.blanket.s02|PMA-秒秒测智能低压电热毯（单人）|67375|
|mibo.valve.001|CNMiBO智能导轨式通断器(控制继电器)AT-SY1|27795|
|miensi.bed.m100|米恩斯智能床M100|33033|
|miga.curtain.mm25te|MM智能电动窗帘25TEIXM|18309|
|milizn.curtain.mili2|XM电动窗帘|12335|
|milizn.curtain.ml002|智能电动卷帘|16102|
|milizn.curtain.ml005|电动智能窗帘(MESH)|22291|
|milizn.curtain.ml009|ml智能窗纱电机|24562|
|milizn.wopener.ml006|V1智能推窗器(Mesh)|22990|
|milizn.wopener.ml03|V1智能推窗器|20413|
|mipin9.curtain.mpcldj|科罗纳窗帘电机（Mesh2.0）|29217|
|miwu.bed.1yznc|1+Y智能床|25826|
|mjkj.curtain.cura01|即米智能窗帘电机J1|26266|
|mjkj.curtain.cura03|即米智能窗帘电机J3|38573|
|mkyb88.curtain.lsk10|K-10mini智能窗帘|37249|
|mlianj.curtain.ct01|MLIANJIA智慧Ai窗帘电机|32733|
|mlily.bed.001|梦百合0压智能床|20546|
|mlily.bed.002|MLILY 0压智能床|31696|
|mlszm.curtain.m82c|MLS云幕智能窗帘电机|38686|
|mlszm.curtain.mlsm3|MLS云隐智能窗帘电机|38687|
|mly.curtain.cura01|魔力云智能窗帘电机|6159|
|mnlqjd.curtain.mnll|迈奈洛智能窗帘|31271|
|mpe.mattress.xmgjb|MPE智能床垫|13926|
|mrbond.curtain.rac03|邦先生智能窗帘|1879|
|msuen.valve.czc25|msuen漏水保护智能阀CZC25/XM|22187|
|musi.bed.bzz1|慕思电动床BZZ1-128|24735|
|musi.bed.v1|慕思智能床BZZ1-128A|36321|
|musi.bed.v2|慕思智能床BZZ1-131|36383|
|musi.bed.v6znc|V6家居智能床BFD1-051|33454|
|musi.bed.v6znc2|V6家居智能床BFD1-050|34082|
|musi.mattress.mw1|慕思AI床垫MWI1-033|24734|
|musi.sofa.v6znsf|V6家居智能沙发 RFA1-655|33471|
|muxnw.dryer.m69|慕向晴风干衣机M69|22375|
|muxnw.dryer.m73|慕向暖流烘鞋器M73|23131|
|mxiot.motor.mxv2|MXAI射频控制器|27381|
|mxsw.curtain.cura01|满星思维S1-mini窗帘电机|34852|
|mxsw.curtain.v1|满星思维S1智能卷帘电机|35178|
|my1234.sofa.my001|迈玥智能沙发|37026|
|nancii.toothbrush.t600|兰希声波电动牙刷T600|5991|
|nbaldq.blanket.zg328|志高水暖毯|33527|
|nbsxh.blanket.dzsnt8|苏宁宜品智能水暖毯|15959|
|nbxh.curtain.cura1|JOCO窗帘电机JM82（Mesh 2.0）|30301|
|nbym.curtain.yznv1|云智能电动窗帘|3331|
|nkkj.dryer.p1|nk净鞋机P1|33293|
|novo.curtain.e38|智能日夜帘|18664|
|novo.curtain.e40|NOVO-升降帘电机|28573|
|novo.curtain.e65|NOVO-前后双排智能窗帘|34720|
|novo.curtain.k25|高端Ai智能卷帘|17048|
|novo.curtain.kx5|NOVO-智能卷帘电机|34277|
|novo.curtain.le40|NOVO-升降帘电机L|32322|
|novo.curtain.m21|N21智能开合电机(MESH)|17120|
|novo.curtain.n20|N23开合电机|14881|
|novo.curtain.n21|Ai智能窗帘电机|4885|
|novo.curtain.n30|NOVO-N31变色氛围灯窗帘|23613|
|novo.curtain.n31|N31氛围灯窗帘|20557|
|novo.curtain.n51|NOVO-左右分控智能窗帘|37902|
|novo.curtain.n99|NOVO-迷你智能窗帘|30091|
|novo.curtain.n99l|NOVO-锂电池迷你窗帘|31859|
|novo.curtain.p2|NOVO-Q2变色氛围灯梦幻帘|24390|
|novo.curtain.q2|Q2氛围灯梦幻帘-Novo|22153|
|novo.curtain.q4|NOVO-Q1梦幻帘电机|36092|
|nowoo.curtain.cura01|华品智能窗帘G15|38593|
|nowoo.curtain.lwm5|乐蜗智能窗帘G20(Mesh2.0)|33017|
|nowoo.curtain.yf02|华品智能窗帘G20（mesh2.0）|37304|
|nvcsmt.curtain.bjj103|雷士照明灵机系列窗帘电机|31548|
|nwer.blanket.nwe01|暖维尔智能电热毯（WiFi）|32214|
|olohas.bed.ogawa8|N次方护脊床垫|9642|
|opa.curtain.jl01|苏驰电动卷帘JL-1|27618|
|opa.wopener.03|苏驰内开内倒窗NKND-1|21334|
|opa.wopener.05|苏驰智能电动窗ZNDD-1|24472|
|opa.wopener.06|苏驰电动窗开窗器ZNDD-1|33088|
|opa.wopener.07|苏驰内开内倒窗开窗器NKND-1|33192|
|opk.motor.djkz|OPK智能滑轨电机控制器|30611|
|oppein.curtain.yf01|海烈鸟H3智能窗帘电机|38365|
|opple.curtain.0021d1|OPPLE 智能窗帘电机|82979|
|pak.curtain.cura1|三雄极光Pak 智能窗帘电机|30800|
|pinhe.motor.ph01|平和智能卷帘门控制器|33727|
|pmfbj.wopener.sxtcq|松下智能窗控制器|32225|
|psd.curtain.psdcm1|PSEIDER PLC卷帘电机|82858|
|ptx.curtain.f1pro|平头熊F1 Pro超薄隐形电机|36280|
|pzg.motor.0006|LKRQ手指机器人（按键）|28703|
|qckj.wopener.zlfkc|智乐福智能电动开窗器|24652|
|qdmyk.beauty.mry01|SeeMagic智能快闪脱毛仪|5666|
|qimi.curtain.cura01|邮科通信智能开合帘|19777|
|qindao.blanket.1905|琴岛智能电热毯|3141|
|qjiang.curtain.gs01|ML智能双电机窗帘V2|26214|
|qjiang.curtain.ml001|ML智能窗帘Mesh2.0|26356|
|qjiang.curtain.ml002|ML智能电动窗帘V3|26527|
|qjiang.curtain.ml003|ML智能双电机窗帘Mesh2.0|26979|
|qjiang.curtain.wsd001|威仕达蓝牙mesh智能开合帘|21928|
|qjiang.curtain.wsd002|威仕达蓝牙mesh智能梦幻帘|22280|
|qjiang.curtain.wsd003|威仕达蓝牙mesh智能双子星开合帘|23264|
|ql0782.bed.001|悬浮云端智能床KLST|18324|
|ql0782.bed.dlxc|朵兰新巢智能床 N1|27007|
|ql0782.bed.donday|德庭助眠智能电动床|22314|
|ql0782.bed.kepler|GOCHEAL广巢智能床|22399|
|ql0782.bed.klstp|KLST克丽斯汀助眠按摩智能床垫Pro|25585|
|ql0782.bed.mx|米象家居悬浮智能床|23370|
|ql0782.bed.sfn|SOFALAND索菲尼智能床|26174|
|ql0782.bed.smui|SMUI敏升智能床|22672|
|ql0782.bed.tqg|智能床|22400|
|ql0782.sofa.001|KLST 克丽斯汀云端智能沙发|19669|
|ql0782.sofa.knoss|GOCHEAL广巢智能沙发|22355|
|ql0782.sofa.pinluo|品洛智能沙发|26365|
|ql0782.sofa.sfn|SOFALAND 索菲尼智能沙发|26366|
|qmlj.sofa.sj001|世茄智能沙发|34823|
|qrua.bed.qrua01|巢物 撑腰电动床|34175|
|qrua.bed.qrua02|巢物 撑腰电动床|35995|
|qshui.blanket.d1|塞问智能水暖床垫|6375|
|qushui.bed.001|8H Milan智能电动床|2001|
|qushui.bed.002|8H自适应软硬可调智能床垫|3264|
|qushui.bed.003|8H Milan智能电动床Pro|3263|
|qushui.bed.004|8H AI人工智能助眠床垫Damo|4011|
|qushui.bed.007|8H Feel真皮智能电动床X Pro|6721|
|qushui.bed.008|8H Feel真皮智能电动床X / +|7869|
|qushui.bed.009|8H Milan智能电动床Pro Max|10580|
|qushui.bed.010s|8H Feel生态皮智能电动床F系列|12387|
|qushui.bed.8hai1|8H AI睡眠监测改善床垫|4918|
|qushui.bed.cw1|趣睡智能床-储物版|31844|
|qushui.bed.de1|8H Find智能电动床|15168|
|qushui.bed.de2|8H Find智能云感悬浮电动床|16811|
|qushui.bed.de2max|8H Star六电机撑腰智能电动床|38067|
|qushui.bed.de2pro|8H Find S五电机撑腰智能悬浮电动床|30130|
|qushui.bed.demax|8H Find智能电动床 Pro|20379|
|qushui.bed.dt31|8H Milan智能电动床 Ultra|19634|
|qushui.bed.dt4|8H Milan智能真皮电动床S|5842|
|qushui.bed.dt7|8H Feel 智能真皮悬浮电动床X+|15355|
|qushui.bed.hjdt8|8H Twins 双分区智能电动床|17143|
|qushui.bed.ma006|8H AI智能撑腰护眠床垫Zero A2|19897|
|qushui.bed.okin1|8H Steady 稳稳智能床|37196|
|qushui.bed.syt|8H Milan City 智能床 Pro max|26405|
|qushui.bed.tvbed1|8H 趣睡智能床 ONE|22878|
|qushui.bedstand.box|8H 趣睡智能多用床头柜G1|18593|
|qushui.blanket.8h|8H 小静智能恒温除螨水暖垫|14155|
|qushui.blanket.8hz1|8H 深睡智能电热毯Z1|29859|
|qushui.blanket.g2|薄床垫|5715|
|qushui.blanket.g22|8H石墨烯智能控温3D薄床垫|11443|
|qushui.blanket.g3|8H 石墨烯智能控温床垫|5716|
|qushui.blanket.snt1|8H 小静智能恒温除螨水暖垫Plus|22323|
|qushui.dryer.8gxg1|8H Free智能护理除菌除臭鞋柜|3730|
|qushui.mattress.mt|8H 5D助眠按摩床垫/S|13837|
|qushui.mattress.mt2|8H 智能助眠按摩床垫|23307|
|qushui.mattress.mtx|8H 智能助眠按摩床垫（石墨烯加热版）|23308|
|qushui.mattress.zeroa1|8H AI智能柱呵护床垫PRO|16921|
|qushui.mattress.zerox|8H AI智能好睡眠床垫X|32500|
|qushui.pillow.mj02|米家智能枕|8411|
|qushui.pillow.p2|8H智能助眠天然乳胶枕X|6371|
|qushui.sofa.001|8H Master 大师智能电动组合沙发|3539|
|qushui.sofa.003|8H COZY智能按摩沙发|7209|
|qushui.sofa.004|8H kola智能电动休闲沙发|9277|
|qushui.sofa.007|8H 智能电动多功能电竞沙发|15366|
|qushui.sofa.b015|8H LINK 模块化沙发|34013|
|qushui.sofa.b7|8H 乐轻松智能电动慢摇沙发|9782|
|qushui.sofa.cloud|8H云朵智能懒人功能沙发|38044|
|qxgk.curtain.ct05|琦星智能开合帘窗帘电机QT801|25387|
|qxgk.curtain.qt605|琦星智能开合帘窗帘电机 QT605|29211|
|qxgk.curtain.qt701|琦星小魔方窗帘电机QT701|29005|
|qykj66.curtain.v2|骐远管状电机TM(Mesh2.0)|35530|
|raex.curtain.a1ksd|科思顿智能窗帘Smart6（低功耗版）|26171|
|raex.curtain.cura01|科思顿智能窗帘Smart6|25751|
|raex.curtain.cura03|Raex智能窗帘电机2.0|31545|
|raex.curtain.le1xa|邦先生智能开合帘|9897|
|raex.curtain.rksjl|Raex卷帘电机（Mesh2.0）|30348|
|raex.curtain.rxcldj|Raex智能窗帘电机Mesh2.0|31266|
|raex.curtain.v1|Raex智能开合帘电机mesh2.0|36274|
|raex.curtain.v2|Raex智能开合帘电机MP82（Mesh2.0）|36273|
|raex.curtain.v3|Raex智能窗帘Mesh2.0|36973|
|rjxn20.curtain.v1|RJ窗帘电机08|37149|
|rjxn20.curtain.v2|RJ窗帘电机03|37150|
|rmt.bed.asbed|Asnug爱舒智慧床|15813|
|rmt.bed.zhsbd2|芝华仕腰托智能床|15814|
|rmt.bed.zhsbd3|芝华仕按摩智能床|20851|
|rmt.bed.zhsbed|芝华仕智能床|3717|
|rnlo01.curtain.cura1|瑞奈智能 窗帘电机2.0|32710|
|ronco.curtain.pro|容科智能窗帘Ultra (Mesh2.0)|31817|
|ronco.curtain.rc120|智能窗帘|6258|
|ronco.curtain.rc160|容科智能窗帘Ultra（Wi-Fi）|22398|
|ronco.curtain.rc181|容科智能窗帘Ultra（Mesh）|22341|
|rtzn.curtain.cura1|睿态智能窗帘电机(Mesh2.0)|30701|
|saila.curtain.sle|智能卷帘电机|11031|
|sanmei.valve.s1|Eztofa智能重合闸通断器L2|23386|
|satori.bed.sd01|世道智能床|27746|
|sayso.curtain.cura01|SAYSO智能窗帘电机|15190|
|sayso.curtain.cura02|SAYSO开合帘电机Mesh版|22732|
|scc.curtain.ct09|西蒙隐藏式开合帘窗帘电机|26190|
|scc.curtain.ct11| Simon无线智能开合帘隐藏款电机|33646|
|scisto.curtain.ct01|科思顿卷帘空心杯25窗帘电机|34151|
|scisto.curtain.d9|科思顿智能窗帘D9|27656|
|scisto.curtain.d92|科思顿分控智能窗帘D9 Air|37350|
|scisto.curtain.ksd01|科思顿智能窗帘Mesh2.0|31914|
|scisto.curtain.wsd|科思顿智能窗帘Smart Air|37529|
|scisto.curtain.xm001|讯米mini6无刷智能窗帘|26592|
|scisto.curtain.yf01|科思顿日夜帘空心杯窗帘电机|39280|
|sdzy.curtain.dt170|世典智能窗帘TGYD|5754|
|sealy.bed.dream|丝涟智眠智能床|39467|
|sfl.curtain.fsldj|FSL 智能82式开合帘电机|32224|
|sfy.bed.b001|索菲亚智能床M1|24997|
|sfy.curtain.c001|索菲亚智能窗帘M1|24083|
|sfy.curtain.c002|索菲亚智能窗帘M1|32809|
|sfy.curtain.c003|索菲亚智能窗帘M2|35622|
|sfy.mattress.m001|索菲亚智能床垫二代单人版|28012|
|sfy.mattress.m002|索菲亚智能床垫二代双人版|28310|
|sfy.mattress.m004|索菲亚智能床垫M1|36085|
|shql.curtain.qlq7|青菱Q7mini智能窗帘电机Mesh2.0|30644|
|shuoda.valve.m1l|TS导轨式开关M1-L|27073|
|shus.bed.a01|Sleepone AI智能床垫|18694|
|shus.bed.bed01|舒是智能电动床|20464|
|shuse.motor.sr03|树色卷帘门电机控制器（Mesh2.0）|38015|
|shuse.roller.sr01|树色卷帘门开关|21963|
|shuse.valve.svc021|树色阀门机械手Pro（Mesh2.0）|29622|
|shuse.valve.svc04|树色智能阀门机械手（Mesh2.0）|29235|
|shuse.valve.svc05|树色阀门机械手|14711|
|shuse.valve.svc10|树色阀门控制器（Mesh）|25657|
|shuse.valve.svc101|树色球阀控制器（Mesh2.0）|37679|
|shuse.valve.svc40|树色阀门机械手3（Mesh2.0）|38845|
|shyzl.blanket.001|俞兆林智能水暖毯|28865|
|shyzl.blanket.sk001|俞兆林智能双控电热毯|29836|
|signfy.curtain.bm0yz1|飞利浦智能窗帘电机_Mify LA100|34280|
|skr003.curtain.ct99|尚科然智能窗帘电机B3|35266|
|skr003.curtain.lsm3|尚科然智能窗帘电机S3|35268|
|skyrc.bed.nest|湃妮冷暖沙发|5296|
|slf.curtain.clsw01|智拉斐零火单路窗帘开关|8081|
|slf.curtain.zlfct|智拉斐82式开合帘窗帘电机|35290|
|smartj.curtain.sjcmnp|SmartJoy极智窗帘电机（蓝牙Mesh版）|18626|
|smartj.curtain.sjcmns|SmartJoy智臻窗帘电机（WiFi版）|3767|
|smartj.curtain.sjd82p|SmartJoy智能窗帘电机（WiFi升级版）|70661|
|smartj.curtain.sjdt82|SmartJoy智能窗帘电机（WiFi版）|68502|
|smartj.curtain.sjscmm|SmartJoy智臻窗帘电机（蓝牙Mesh版）|8199|
|smith.blanket.cxma1| 佳尼特恒温水暖床垫 CXM-A1|1361|
|soocare.toothbrush.1501|米家声波电动牙刷T501|8179|
|soocare.toothbrush.x3|素士声波电动牙刷|206|
|stesh.blanket.rug02|YNXT恒温地暖垫|17517|
|sunica.curtain.6901|SUNICA SN6901智能窗帘电机 mesh|40451|
|sunica.curtain.s8|SUNICA智能窗帘S8 Mesh2.0|32981|
|sunica.curtain.sn06|SUNICA SN06智能无刷窗帘电机 mesh|39371|
|sxds.blanket.jssn01|简色智能水暖床垫（双温控）|3111|
|sxds.blanket.jssncd|简色智能水暖床垫(单温控)|2969|
|sxds.pillow.pillow02|天然乳胶智能助眠枕|67890|
|sxyk.curtain.sxs7|素昔智能窗帘电机U7mini|30645|
|sym.motor.dctl01|尚阳梦智能门远程控制器RF01|30356|
|sym.motor.dctl02|尚阳梦卷帘门智能控制器JLM1|33648|
|symi.curtain.ct06|亖米智能窗帘电机|25440|
|symi.curtain.cura01|亖米智能窗帘mesh版|10057|
|symi.curtain.cura02|晓翼智能窗帘mesh版|16897|
|symi.curtain.cura03|亖米Mesh智能窗帘Ultra|24698|
|symi.curtain.cura04|晓翼Mesh智能窗帘Ultra|24704|
|symi.curtain.cura05|亖米Mesh智能窗帘电机Ultra|28623|
|symi.curtain.cura06|晓翼Mesh智能窗帘电机Ultra|28625|
|syniot.curtain.m1|居意电动卷帘|69516|
|syniot.curtain.syc1|居意电动窗帘|66301|
|tfc.bed.001|添康智能床|21380|
|thm11.blanket.2308|泰和美智能恒温水暖床垫|16852|
|thm11.blanket.ln2401|泰和美冷暖床垫青春版|16227|
|timi.motor.tmdj|天米电机控制器（WiFi）|35709|
|tld.wopener.py001|拓利达智能推拉窗开窗器TZD-PY01|24250|
|tms.dryer.sbhxj|沙伯智能烘鞋器|30426|
|tmwl.valve.iotb2|透明物联网漏电断路器IOTB2|24731|
|tofan.curtain.ct03|悠觅隐形窗帘电机M3-PRO2.0|32335|
|tofan.curtain.ct04|悠觅觅隐窗帘电机|38305|
|tofan.curtain.ct06|YOOMI智能窗帘电机MESH2.0|26704|
|topwit.curtain.rzct01|UZ窗帘电机|17440|
|topwit.curtain.rzct04|UWIZE优智者窗帘电机|27198|
|trdz01.blanket.dkdrt|AOTEYOU智能单控加热毯|30011|
|trdz01.blanket.skdrc|AOTEYOU智能双控加热毯|30010|
|tsk.wopener.tsk01|特斯卡智能开窗器|33197|
|tstar.razor.ra2|VTT高端剃须刀|15412|
|ttzn.curtain.tta6|拓泰智能窗帘A6|26879|
|tzd.wopener.nknd|拓智达隐藏式开窗器TZD-NKND|21617|
|tzd.wopener.tzdlt|拓智达智能开窗器TZD-LT|23798|
|uehome.sofa.imi1|UE  艾米智能按摩沙发|9078|
|uimeen.valve.fmp1|钻石阀门控制器（WiFi）|32777|
|uimeen.valve.zsfm|钻石阀门控制器|24324|
|uimeen.valve.zsfm20|钻石阀门控制器（Mesh2.0）|29051|
|unec.curtain.cura01|UNEC智能窗帘电机|31733|
|uvfive.dryer.panda|FIVE智能烘鞋暖被干衣机|4081|
|uxkeji.curtain.40tt|智帮手智能开合帘|9511|
|uxkeji.curtain.50tt|智帮手智能卷帘|10731|
|uxkeji.curtain.63att|智帮手智能开合帘（蓝牙Mesh版）|16452|
|uxkeji.curtain.gmkhl|GM智能开合帘|73530|
|viomi.curtain.v1|云米互联网窗帘电机（Wi-Fi版）|66869|
|viomi.curtain.v2|云米互联网窗帘电机 Auto 1A|4428|
|viomi.curtain.v3|云米AI智能窗帘电机Auto 1S|7024|
|viomi.curtain.v4|云米AI智能窗帘电机Smart|13335|
|viomi.curtain.v5|云米AI智能窗帘电机Master|16952|
|walter.blanket.2022|沃尔特赫恩恒温水暖毯|10988|
|wanrui.blanket.psn2a|质零智能水暖床垫|5963|
|wczn11.wopener.vc001|唯楚开窗器|24197|
|wenxi.hair.5000w|早鱼智能吹风机MMD-5000W|29340|
|wfxx.motor.lsmk|麒石门控|12265|
|wfxx.motor.mxrf|MX射频控制器PLUS|16565|
|wfxx.motor.qsmkdm|麒石电机控制器|21550|
|wfxx.motor.ycmkq|MX射频控制器|11794|
|wgse.curtain.cl1r01|WGSE智能窗帘电机|38425|
|wintom.curtain.230xm|创明智能窗帘|1541|
|wintom.curtain.ag25|创明智能成品帘AG25|35224|
|wintom.curtain.ag35|创明智能成品帘AG35|35225|
|wintom.curtain.cmcl1|创明智能窗帘电机M1|32669|
|wintom.curtain.cmcldj|创明智能窗帘电机Mesh2.0|30126|
|wintom.curtain.cq3|创明智能窗帘电机CQ3|37067|
|wintom.curtain.cura09|创明智能窗帘电机Q5|36666|
|wintom.curtain.cura10|创明智能窗帘电机A5 Pro|36912|
|wintom.curtain.cura11|创明智能窗帘电机A5|37081|
|wintom.curtain.cura8|创明Mesh2.0智能窗帘电机|32445|
|wintom.curtain.v1|创明智能窗帘电机180|36271|
|wlnkj.curtain.ct06|未来鸟鸥璃窗帘电机D2|27174|
|wsd.curtain.ct01|威仕达智能日夜帘窗帘电机-蓝牙Mesh2.0|28742|
|wsd.curtain.ct02|威仕达隐藏式开合帘窗帘电机-蓝牙Mesh2.0|28743|
|wsd.curtain.ct03|威仕达智能管状窗帘电机-蓝牙Mesh2.0|28744|
|wsd.curtain.ct044|威仕达智能开合帘窗帘电机-蓝牙Mesh2.0|28952|
|wsd.curtain.wscmbr|威仕达天锐星无刷窗帘电机|40670|
|wsd.curtain.wscmxi|威仕达隐藏式窗帘电机-蓝牙Mesh2.0|37696|
|wsd.curtain.wscmxj|威仕达无刷双子星窗帘电机WSCMXJ-BR|39083|
|wsd.curtain.wscmxk|威仕达天微星无刷窗帘电机|38807|
|wsd.curtain.wsd005|威仕达智能双子星开合帘蓝牙mesh2.0|27688|
|wsd.curtain.wushua|威仕达隐藏式无刷开合帘窗帘电机|37532|
|xcmc.wopener.xcyg|晓晨智能开窗器XC-60|28014|
|xfl.motor.v1|典一电动门电机控制器|25480|
|xhjtkj.bed.e10|智安舒智能床-e10|33133|
|xhjtkj.bed.e10pro|智安舒智能床-e10pro|35535|
|xhjtkj.bed.e10rs|智安舒智能床-e10rs|31917|
|xhjtkj.bed.m10|智安舒智能床-m10|37167|
|xhjtkj.bed.m11|智安舒智能床-m11|37920|
|xhuan.curtain.ct01|苏米星轨电机Mesh2.0|30774|
|xhuan.curtain.cura02|苏米智能窗帘电机 T1|4943|
|xhuan.curtain.cura03|苏米智能窗帘电机 T1  Pro|4985|
|xhuan.curtain.cura04|苏米开合帘电机（蓝牙Mesh版）|13383|
|xhuan.curtain.cura05|苏米梦幻帘|15164|
|xhuan.curtain.cura06|苏米智能开合帘电机Mesh2.0|24986|
|xhuan.curtain.cura08|苏米隐藏式窗帘电机Thor|28886|
|xhuan.curtain.plcg01|苏米智能开合帘电机PLC版|80835|
|xhuan.curtain.v1|苏米全隐藏电机|35943|
|xhuan.curtain.v2|苏米全隐藏电机（无刷版）|37633|
|xhuan.curtain.wyrz12|苏米智能开合帘Mesh2.0|27426|
|xiaomi.blanket.mj1|米家智能电热毯|15627|
|xiaomi.blanket.mj7|米家智能电热毯|30935|
|xiaomi.curtain.003|米家智能窗帘 3 Pro|29591|
|xiaomi.curtain.0303|米家智能窗帘 3|36980|
|xiaomi.curtain.acn009|米家智能窗帘 伸缩轨道版|14195|
|xiaomi.curtain.acn010|米家智能窗帘2|18699|
|xiaomi.curtain.acn012|米家隐藏式智能窗帘|22476|
|xiaomi.curtain.g10|米家隐藏式智能窗帘 G10|24557|
|xiaomi.toothbrush.p002|米家多向扫振电动牙刷Pro|28507|
|xijia1.curtain.c10|玺加智能窗帘C10|35989|
|xijia1.curtain.c11|玺加左右分控开合窗帘C11|35903|
|xijia1.curtain.c9|玺加智能窗帘C9|23562|
|xijia1.curtain.ck3xwb|玺加智能窗帘C3|11631|
|xijia1.curtain.cr1|玺加智能窗帘模块CR1|12574|
|xijia1.curtain.m8|玺加智能窗帘C8|11266|
|xijia1.curtain.x3|玺加智能窗帘宝X3|19363|
|xinji.curtain.cura01|新极智能窗帘电机|17080|
|xinyue.blanket.n1918|绘睡一键舒眠水暖垫|1723|
|xjiang.curtain.kddm12|科大龙创蓝牙mesh智能窗帘电机|25775|
|xjyd.toothbrush.k1|亲天K1-MI声波电动牙刷|13282|
|xlm.mattress.h11cc|喜临门呼呼智能床垫H300|35519|
|xm008.curtain.dy01|摩亨智能窗帘电机|12068|
|xm008.curtain.dyclm|科真窗帘电机（Mesh2.0）|28890|
|xmlong.toothbrush.r02|西马龙电动牙刷R02|12439|
|xmlong.toothbrush.r05|西马龙电动牙刷R06|12486|
|xql.sofa.sofa01|载起智能沙发|30928|
|xumei.razor.str212|须眉便携电动剃须刀|14789|
|xwiwn.curtain.xwc001|xiaowell小为科技智能窗帘电机|35892|
|yakino.curtain.ct01|雅琪诺隐藏式智能窗帘电机|33681|
|yakino.curtain.ct02|美绮隐藏式智能窗帘电机|36678|
|yakino.curtain.e10|雅琪诺智能窗帘|7359|
|yankon.curtain.ygsm2|阳光智能窗帘电机M1|33791|
|yeelink.curtain.crc1|Yeelight 智能开合窗帘电机|10813|
|yeelink.curtain.crc10|Yeelight Z2智能无刷开合帘电机|34869|
|yeelink.curtain.crc11|Yeelight T系列直流百叶帘电机|37929|
|yeelink.curtain.crc12|Yeelight T系列直流卷帘电机|37936|
|yeelink.curtain.crc16|Yeelight Z1 Lite智能开合帘电机|40003|
|yeelink.curtain.crc2|Yeelight 智能开合帘电机C2（WIFI版）|11025|
|yeelink.curtain.crc3|Yeelight 智能开合帘电机|16381|
|yeelink.curtain.crc4|Yeelight 智能开合帘窗帘电机|16911|
|yeelink.curtain.crc5|YEELIGHT凌动 开合窗帘电机|17291|
|yeelink.curtain.crc6|Yeelight SU智能窗帘电机|20547|
|yeelink.curtain.crc7|Yeelight 智能窗帘电机2.0|22845|
|yeelink.curtain.crc8|Yeelight 隐藏式无刷窗帘电机|26511|
|yeelink.curtain.crc9|Yeelight 智能窗帘电机SU ultra|26674|
|yeelink.curtain.ctmt1|Yeelight 智能 窗帘电机|1548|
|yeelink.curtain.ctmt2|Yeelight 快装窗帘|7961|
|yeelink.curtain.ywc01|Yeelight Pro 窗帘|5718|
|ygzm.curtain.cura01|杜蒙智能窗帘电机X1Pro|36682|
|yier.mosq.v1|KIMEEY智能电蚊拍|36584|
|yifang.mosq.yx01|智能除螨驱蚊器|13340|
|yilock.curtain.yilc3|Yi-Lock小益智能窗帘|69944|
|yiree.bed.yibed1|谊瑞智能床|15477|
|ykbn.curtain.k9|YKBN智能窗帘电机|5274|
|ykbn.curtain.yksy|YKBN双隐智能窗帘|34475|
|ykcn.valve.01|YKCN 智慧用电电源 TTDZ-63A|23722|
|ykcn.valve.cbcs|智能导轨式通断器YKCN|19951|
|ykcn.valve.rdb7h|Wi-Fi智能导轨式断路器YKCN|20090|
|ykj.sofa.sofa01|EQY智能沙发|33693|
|ykl.bed.bed01|晶米智能床|27945|
|ykl.curtain.cura1|晶米智能窗帘电机mesh版|30051|
|ylsy01.bed.znc408|雅兰智能床AC-408|30893|
|ylyd.blanket.sk1000|伊露亚迪水暖毯|6901|
|ym001.dryer.ymgyj|炎米智能便捷干衣机|31165|
|ym001.dryer.ymhxq|炎米智能烘鞋器|32256|
|ym001.mosq.dwpy1|炎米智能便携电蚊拍Y1|36355|
|ym001.mosq.dwpy2|炎米智能电蚊拍Y2|36356|
|ym001.mosq.ymdwp|炎米智能电蚊拍（WiFi）|25324|
|ym001.mosq.ymdwpu|炎米智能电蚊拍Ultra（WiFi）|27904|
|ym001.mosq.ymqw|炎米智能驱蚊器|26923|
|ym001.mosq.ymqwb|炎米智能驱蚊器 Y1|37826|
|ym001.mosq.zndwp|炎米智能电蚊拍Y1|35854|
|ym001.razor.my22|炎米赛博剃须刀 X1 探索版|38630|
|yms1.curtain.cura01|悠漫时T9隐藏式窗帘电机|37488|
|ymwl.curtain.cura01|一米未来智能窗帘电机M1|6585|
|yoohoo.curtain.ct06|FRFOX-LS窗帘电机|25439|
|youha.breast.s1|优合S1吸奶器|14052|
|yszh.wopener.bs817|智能推窗器|9430|
|yszh.wopener.ys01|YUSHUN智能开窗器|29193|
|yunmi.curtain.v6|云米隐藏式窗帘电机Mini|28364|
|ywl.motor.ywlmm|易我联电机控制器（Mesh2.0）|34762|
|yxsm01.blanket.jrdrt|冀人智能电热毯（WiFi）|27376|
|yyunyi.wopener.pk1|云仪智能开窗器电池版PK1|31776|
|yyunyi.wopener.yylt|云仪链条开窗器|5783|
|yyunyi.wopener.yypy24|云仪平移开窗器|66793|
|yzjkj.motor.dmc1|麒石多门遥控器D1|31829|
|yzjkj.motor.f1|麒石BLE电机控制器F1|33794|
|yzjkj.motor.yzjkj|麒石单门控制器A1|29289|
|yzjkj.motor.yzjmk|麒石多门控制器A3|29552|
|zbom.curtain.yf01|志邦隐藏款智能窗帘电机|39334|
|zemi.curtain.lzv3|Zemismart拉珠窗帘电机V1|26903|
|zemi.curtain.zm25|Zemismart智能卷帘电机|9363|
|zemi.curtain.zm85|ZM智能窗帘|17182|
|zemi.curtain.zmcldj|Zemismart窗帘电机|33651|
|zhenji.wopener.zj1q|圳基锂电开窗器|36590|
|zhenji.wopener.zj2q|圳基门窗电机|38088|
|zhiee.curtain.bjcl1|百将窗帘伴侣|31821|
|zhij.toothbrush.bv1|修然得体智能感应杀菌杯|2378|
|zhitai.curtain.xgp|智泰智能电动窗帘ZT-99|35499|
|zhitai.curtain.zt01|ZT双胞胎开合帘电机|39956|
|zhj.curtain.cura01|智和家 静音智能窗帘电机2.0|26022|
|zhj.curtain.cura02|智和家 K6迷你智能窗帘电机|37052|
|zhj.curtain.cura03|智和家 T6静音智能窗帘电机|37053|
|zhj.curtain.zhj928|智和家 玲珑智能电机|20076|
|zhj.curtain.zhj929|智和家 玲珑智能电机Pro|23844|
|zhj.curtain.zhj930|智和家 迷你智能窗帘电机|25966|
|zhj.curtain.zhj931|智和家 玲珑智能窗帘电机2.0|32534|
|zhtech.curtain.zhcl|ZH智能窗帘电机|27393|
|zhtech.curtain.zhjldj|ZH卷帘电机|29346|
|zhtech.curtain.zm25s|智皇智能卷帘电机|8732|
|zhtech.curtain.zm83|智皇开合窗帘电机|8580|
|zhtech.curtain.zm83s|ZH智能窗帘（Mesh)|16683|
|zinguo.motor.mk01|卷帘门控制器|11468|
|zjcr.razor.rs158|超人智能剃须刀HS158|16289|
|zjcr.razor.rs7368|超人智能剃须刀|12862|
|zjdh.curtain.xj001|XM智能电动窗帘|15087|
|zjdh.curtain.xj002|智能电动窗帘(Mesh)|17659|
|zjjc.curtain.ct01|金蝉智能窗帘电机 · 光影大师|35712|
|zjjc.curtain.yf02|金蝉 · 小魔方 无刷隐藏式窗帘电机|37528|
|zksq.curtain.cura01|SWAN HOME智能窗帘电机|27984|
|zlx.curtain.zlxcl|智领袖智能窗帘电机|33031|
|zlyj88.curtain.ypdj1|雁派智能开合帘电机|32667|
|zlyj88.curtain.ypdj2|雁派智能窗帘电机|33514|
|zlyj88.curtain.ypdj3|雁派智能窗帘电机mini|35143|
|znsn.curtain.ct06|正尚82型窗帘电机|25599|
|znsn.curtain.zsct01|ZNSN正尚窗帘电机|21464|
|zrsd.motor.ddm01|ZRSD卷帘门控制器|29216|
|zs1001.mosq.s12pro|质零数显电蚊拍-Wifi款|5496|
|zs1001.mosq.ymdwp|质零数显电蚊拍-WiFi升级款|26399|
|zuka.curtain.cura01|佐卡智能 窗帘电机2.0|26023|
|zw1688.blanket.01dk|LWU单控电热毯|32498|
|zw1688.blanket.01sk|LWU双控电热毯|32497|
|zyj01a.curtain.zycl2|智越佳智能窗帘伴侣|33789|
|zzslc.curtain.slc02|松联诚智能窗帘电机|31655|

### 传感器

|model|name|pd_id|
|---|---|---:|
|090615.sensor_occupy.mw|PTX 人体存在传感器|16168|
|090615.sensor_occupy.xw|平头熊人体存在传感器(顶装版)|18736|
|ainice.motion.bt|AInice人体传感器|6860|
|ainice.sensor_occupy.3b|AInice三体场景传感器|18672|
|ainice.sensor_occupy.bt|AInice电子围栏传感器|10980|
|ainice.sensor_occupy.rd|AInice双存在传感器|13156|
|anseny.sensor_ht.0121b|Anseny室内温湿度计CX0121B|33427|
|anseny.sensor_ht.0311b|Anseny室内温湿度计CX0311B|28116|
|anseny.sensor_ht.0314b|Anseny室内温湿度计CX0314B|27745|
|anseny.sensor_ht.cx0710|Anseny室内温湿度计CX0710B|27316|
|anseny.sensor_ht.cx920b|Anseny室内温湿度计CX920B|32786|
|anymetre.sensor_ht.th7m|美德时蓝牙温湿度计TH7M|30459|
|bkxh.flood.yf02|小海・久安水浸传感器|38955|
|bkxh.magnet.yf01|小海・久安门窗传感器|38953|
|bkxh.sensor_gas.s2|小海・久安燃气泄露传感器|38929|
|bkxh.sensor_smoke.s1|小海・久安烟雾传感器|38868|
|bogin8.sensor_occupy.bj|柏晶人体存在传感器|34128|
|brains.sensor_occupy.r4|博瑞思人体存在传感器|20434|
|btzn.magnet.v1|比特门磁|71571|
|bull.magnet.yf01|公牛门窗传感器|39356|
|bull.sensor_ht.t01e1c|公牛温湿度传感器|39245|
|bull.sensor_occupy.yf02|公牛人体移动传感器|39358|
|bymiot.magnet.wlv2|未来居无线门窗传感器（粘贴版）|76143|
|bymiot.magnet.wlv3|未来居无线门窗传感器（嵌入版）|76563|
|bymiot.motion.v1|未来居人体移动传感器|67328|
|bymiot.motion.wlv2|未来居无线人体移动传感器|74596|
|bymiot.sensor_ht.v1|未来居有线温湿度传感器|80990|
|bymiot.sensor_occupy.gl|未来居通用存在传感器|76572|
|bymiot.sensor_occupy.v3|未来居强电插卡取电|67701|
|cchome.motion.v1|人体感应器|68351|
|cgllc.magnet.hodor|青萍门窗开合传感器|982|
|cgllc.motion.cgpr1|青萍动作和环境光传感器|2691|
|cgllc.sensor_ht.cgdk3|青萍温湿度计 Lite（7 号电池）|20313|
|cgllc.sensor_ht.cgg3|青萍温湿度计（7 号电池）|22536|
|cgllc.sensor_ht.cgm1|李吉他蓝牙温湿度计|2062|
|cgllc.sensor_ht.dk2|青萍蓝牙温湿度计Lite（纽扣电池）|1647|
|cgllc.sensor_ht.g1|青萍蓝牙温湿度计（纽扣电池）|839|
|cgllc.sensor_ht.qpg1|青萍蓝牙温湿度计（纽扣电池）|2888|
|deli.sensor_ht.523bt|得力蓝牙款电子温湿度计LE523BT|30266|
|dnake.sensor_occupy.cz1|狄耐克人体存在传感器|34248|
|duka.sensor_ht.th2|杜克TH2墨水屏时钟温湿度计|15629|
|ed01.sensor_occupy.ed36|易探人体存在传感器EDQ201-M|33021|
|ed01.sensor_occupy.ytld|易探人体存在传感器EDQ25M|30389|
|evecca.flood.rs001|易慧家雨水传感器3S|21435|
|gaosd.sensor_occupy.grd|高事达PLC人体存在传感器(24G)|80840|
|giot.magnet.mkcgq|SMLK门控传感器|23850|
|giot.magnet.mkcgq1|SMLK门控传感器V1|26018|
|giot.sensor_occupy.v1ps|Gra人体存在传感器V1（BLE）|20872|
|googo.sensor_occupy.cgq|mitch人体存在传感器|32736|
|grom.sensor_occupy.pir|格罗姆红外人体传感器|39470|
|guixin.sensor_ht.wsdu1|U-FAMILY WiFi 温湿度传感器U1|33387|
|hccy.sensor_ht.3bx321|MiKO蓝牙温湿度计|20184|
|hccy.sensor_ht.mikos|MiKO小方形温湿度计|24153|
|hly.sensor_occupy.m04lb|欧微灵科人体红外传感器|31833|
|hly.sensor_occupy.m08lb|欧微灵科人存传感器|33266|
|hx888.sensor_ht.hxwb|兴智连温湿度计|26794|
|iotpfk.flood.001|IoTPERFECT水浸传感器S01D|24569|
|isa.magnet.dw2hl|小米门窗传感器2|2443|
|izq.sensor_occupy.24|子擎存在传感器 Lite|10356|
|izq.sensor_occupy.24n|子擎存在传感器 Ceiling|14495|
|izq.sensor_occupy.ble|子擎存在传感器 Loong|18788|
|izq.sensor_occupy.solo|子擎存在传感器 Solo|14496|
|izq.sensor_occupy.trio|子擎存在传感器 Trio|16357|
|jysj.sensor_occupy.dk21|迪智客存在传感器DK21|24950|
|laidun.sensor_occupy.02|LD人体存在传感器（BLE）|29827|
|laig.sensor_occupy.cgq|小徕智存人体存在传感器|36681|
|lemesh.sensor_occupy.s3|情景存在传感器|13245|
|line.flood.ftw1|方舟鱼水浸传感器TW1|13734|
|line.flood.tw1|LineHope水浸传感器TW1|11448|
|line.magnet.ftm1|方舟鱼门窗传感器TM1|13736|
|line.magnet.tm1|LineHope门窗传感器TM1|11446|
|line.motion.ftr1|方舟鱼人体移动传感器TR1|13735|
|line.motion.tr1|LineHope人体移动传感器TR1|11447|
|line.sensor_ht.fth1|方舟鱼温湿度传感器TH1|13738|
|line.sensor_ht.fth1s|方舟鱼温湿度传感器TH1S|13737|
|line.sensor_ht.th1|LineHope温湿度传感器TH1|11444|
|line.sensor_ht.th1s|LineHope温湿度传感器TH1S|11445|
|linp.flood.rs1bb|领普水浸及雨水传感器|16143|
|linp.magnet.m1|领普门窗传感器|6281|
|linp.motion.h1|领普人体传感器|6284|
|linp.motion.hs1bb1|领普人体传感器2|10987|
|linp.motion.hs1bb2|领普人体传感器3|20692|
|linp.senpres.ps1bb|领普压力有无传感器|16204|
|linp.sensor_ht.ks1bp|领普无线开关KS1Pro|15895|
|linp.sensor_ht.ks2bb|领普温湿度传感器|21003|
|linp.sensor_occupy.es2|领普人体存在传感器ES3|20731|
|linp.sensor_occupy.es2b|领普人体存在传感器ES2|19662|
|linp.sensor_occupy.es4b|领普人体存在传感器ES5（顶装版）|28377|
|linp.sensor_occupy.es5b|领普人体存在传感器ES5|27151|
|linp.sensor_occupy.hb01|领普人体存在传感器|10441|
|linp.sensor_occupy.hb04|人体存在传感器（顶装PLC版）|76474|
|loease.sensor_ht.t49bt|乐易仕智能温湿度计T35|17967|
|lumi.flood.acn001|Aqara 水浸传感器 E1|72751|
|lumi.flood.bmcn01|小米水浸卫士|2147|
|lumi.magnet.acn001|Aqara 门窗传感器 E1|72749|
|lumi.motion.acn001|Aqara 人体传感器 E1|72752|
|lumi.motion.bmgl01|小米人体传感器2|2701|
|lumi.sen_ill.agl01|Aqara光照传感器T1|66501|
|lumi.sen_ill.mgl01|小米光照传感器|65843|
|lumi.sensor_gas.acn02|Aqara 天然气报警器|67295|
|lumi.sensor_gas.mcn02|小米天然气卫士|2456|
|lumi.sensor_ht.v1|小米温湿度传感器|98|
|lumi.sensor_magnet.aq2|Aqara门窗传感器|450|
|lumi.sensor_magnet.v1|门窗传感器|42|
|lumi.sensor_motion.aq2|Aqara人体传感器|451|
|lumi.sensor_motion.v1|人体传感器|43|
|lumi.sensor_natgas.v1|天然气报警器|250|
|lumi.sensor_smoke.acn01|Aqara烟雾报警器（NB-IoT版）|66496|
|lumi.sensor_smoke.acn03|Aqara烟雾报警器|67294|
|lumi.sensor_smoke.mcn02|小米烟感卫士|2455|
|lumi.sensor_wleak.aq1|Aqara水浸传感器|385|
|lumi.vibration.agl01|Aqara动静贴T1|68894|
|lumi.vibration.aq1|Aqara动静贴|386|
|lumi.weather.v1|Aqara温湿度传感器|354|
|lxun.sensor_occupy.cz01|LX存在传感器|13970|
|merryt.sensor_occupy.m1|迈睿人体存在传感器M1|20745|
|miaomiaoce.sensor_ht.a1|秒秒测智能语音闹钟|14599|
|miaomiaoce.sensor_ht.h1|秒秒测蓝牙温湿度计|903|
|miaomiaoce.sensor_ht.t1|小米米家电子温湿度计Pro|1115|
|miaomiaoce.sensor_ht.t2|小米米家蓝牙温湿度计2|1371|
|miaomiaoce.sensor_ht.t4|秒秒测蓝牙温湿度计2|12641|
|miaomiaoce.sensor_ht.t6|小米电子温湿度计|4611|
|miaomiaoce.sensor_ht.t8|小米米家电子温湿度计Pro|9538|
|miaomiaoce.sensor_ht.t9|米家智能温湿度计3|10290|
|mingpu.sensor_gas.det1|云檬宝 燃气报警器|69776|
|mipin.motion.mc1|MIANCHU免触传感器标准版|13167|
|mipin.sensor_occupy.mc2|MIANCHU免触传感器Mesh版|16254|
|mirsz.flood.wa500|罗威亚水浸传感器|6492|
|mirsz.magnet.mc500|罗威亚门窗传感器|6493|
|mirsz.magnet.yf4|罗威亚门窗开关传感器|35862|
|mirsz.motion.ir500|罗威亚红外人体移动传感器|6491|
|mirsz.sensor_gas.ga500|燃气传感器|14637|
|mirsz.sensor_ht.ht02|罗威亚TE700温湿度传感器|33655|
|mirsz.sensor_ht.te110|罗威亚温湿度传感器（无屏）|6490|
|mirsz.sensor_ht.te500|罗威亚温湿度传感器|6489|
|mirsz.sensor_occupy.h01|罗威亚人体存在传感器MIR-HE1-BT|20488|
|mirsz.sensor_occupy.mlk|罗威亚吸顶式人体存在传感器LY-HE300-BT|33302|
|mirsz.sensor_occupy.yf3|罗威亚人体移动传感器|35643|
|mirsz.sensor_smoke.s500|烟雾传感器|14638|
|mlszm.sensor_occupy.rc1|MLS星觅传感器|38697|
|ms2021.sensor_occupy.mg|MG人体存在传感器V2（BLE）|33430|
|ptkj.sensor_ht.e1mini|ProTap蓝牙温湿度计E1mini|33381|
|ptkj.sensor_ht.t1|ProTap蓝牙温湿度计T1|27727|
|qjiang.sensor_ht.002|RSH蓝牙温湿度计|24893|
|qjiang.sensor_occupy.qj|QUMI趣米人体存在传感器|16341|
|rhj.sensor_occupy.l730|乐天派存在传感器Box|16017|
|rhj.sensor_occupy.l730a|乐天派人在传感器POP|20179|
|rhj.sensor_occupy.l730b|乐天派人在传感器Air|21517|
|rhj.sensor_occupy.l730d|乐天派人在传感器POP2|23482|
|rinmin.sensor_occupy.lm|菱敏人在传感器|30486|
|riters.sensor_ht.2351|RITERS温湿度计2351|26301|
|rsh.sensor_ht.1|RSH温湿度计WiFi款|34347|
|rttrp.sensor_gas.jy500|多瑞燃气报警器|6108|
|shuse.flood.ss05|树色水浸传感器（BLE）|19533|
|shuse.flood.ss40|树色水浸传感器Slim（BLE）|30404|
|shuse.flood.sssj|树色水浸传感器Pro（BLE）|27489|
|shuse.magnet.ss03|树色门磁传感器 （BLE）|19531|
|shuse.magnet.ssmc|树色门磁传感器Pro（BLE）|28848|
|shuse.motion.ss20|树色太阳能人体及雨水传感器（BLE）|33517|
|shuse.motion.sshw1|树色人体红外传感器（BLE）|35542|
|sixwgh.flood.sj01|文光汇水浸传感器|35934|
|sixwgh.sensor_ht.v1|文光汇温湿度计|30608|
|sixwgh.sensor_ht.wsdj01|文光汇温湿度计|39340|
|slf.magnet.mc02|智拉斐门磁传感器|34365|
|slf.sensor_occupy.exist|智拉斐人在传感器CG1|38010|
|tad.sensor_occupy.zalrc|智安莱人体存在传感器|35104|
|tofan.sensor_ht.ht01|悠觅温湿度传感器|37672|
|trony.sensor_ht.lvws01|LUMIVATOR光伏智能体感温湿度计LV-WS001|27892|
|uimeen.flood.rmsjb|钻石水浸传感器|25556|
|vchon.sensor_ht.mbs16|目博士温湿度计MBS-16|24721|
|vchon.sensor_ht.mbs17|目博士温湿度计MBS-17|23985|
|vchon.sensor_ht.mbs20|目博士温湿度计MBS-20|32489|
|vchon.sensor_ht.mbs7|目博士温湿度计MBS-7|21585|
|wiing.sensor_ht.wsd01|AImLbS智能温湿度计|38674|
|xhuan.sensor_occupy.s01|苏米存在传感器|11849|
|xiaomi.flood.oh83w|小米水浸卫士2|25461|
|xiaomi.magnet.03|小米门窗传感器3|35845|
|xiaomi.motion.pir1|小米人体传感器2S|13617|
|xiaomi.sensor_ht.mini|米家智能温湿度计3 mini|21941|
|xiaomi.sensor_ht.new3pr|米家智能温湿度计3 Pro|39609|
|xiaomi.sensor_occupy.03|小米人在传感器|18051|
|xiaomi.sensor_occupy.p1|小米人在传感器Pro|19390|
|xiaomi.sensor_smoke.yg2|小米烟感卫士2|31418|
|yeelink.magnet.ycs02|Yeelight Pro 门窗传感器|73195|
|yeelink.motion.ymt02|Yeelight Pro 人体传感器|73194|
|yeelink.sensor_occupy.1|Yeelight Z系列人在传感器|27571|
|yeelink.sensor_occupy.a|Yeelight 人体存在传感器|17160|
|yg1.sensor_ht.sens02|情景门磁温湿度计|33100|
|ygzl.sensor_occupy.s2|圣络维人体存在传感器S2|33664|
|ym001.sensor_ht.ymwsdj|炎米智能温湿度计|30939|
|yoda.sensor_ht.le508|得力温湿度计LE508|16626|
|yongsh.sensor_ht.kd30|温度精灵温湿度计KD30|25595|
|yongsh.sensor_ht.st34|温度精灵温湿度计ST34|30044|
|yongsh.sensor_ht.st60|温度精灵温湿度计ST60|28117|
|yongsh.sensor_ht.st70|温度精灵温湿度计ST70|28119|
|yqll.sensor_ht.dm1095|德力西电气智能温湿度计DM-1095|32343|
|yuemee.sensor_gas.0605|家用可燃气体探测器|3997|
|yuemee.sensor_gas.56712|家用可燃气体探测器|6788|
|yutai.sensor_ht.wsd01|ZUZW智能蓝牙温湿度计|32569|
|zhiee.flood.sj01|USP国际电工水浸传感器|30482|
|zhiee.flood.ys01|百将雨水传感器|34609|
|zhiee.magnet.mc01|USP国际电工门窗传感器|30929|
|zhiee.sensor_ht.wsdj01|百将温湿度传感器|33341|
|zinguo.sensor_ht.t5|峥果温湿度计|32780|
|zipu.sensor_ht.cda05|温心室爱温湿度计ZP-CDA05|27595|
|zksq.sensor_occupy.s2|SWAN HOME人体存在传感器|30989|
|zlyj88.magnet.ypmc1|雁派门磁传感器|32665|
|zywjw.magnet.zmmc|执梦门磁传感器|28591|
|zywjw.sensor_occupy.c01|执梦人体存在传感器|19582|

### 其他

|model|name|pd_id|
|---|---|---:|
|adp.fitting.adgw|艾达普 智能控制伴侣|16892|
|aizbot.etool.xqspkb|Aiasst 智能射频控制器 mini|36359|
|aizbot.etool.zqsp|Aiasst智能射频控制器|28175|
|bymiot.ir.wlv1|未来居无线万能遥控器|72913|
|cddz.etool.jhrfc|Jiuhao射频控制器（WiFi）|32257|
|cddz.etool.jhrfw|Jiuhao射频控制器（Mesh2.0）|35334|
|chuangmi.ir.v2|小米万能遥控器|23|
|duka.etool.hm1|杜克HM1儿童智能身高测量仪|27593|
|elian.etool.f5|锁小宝抽屉柜开关Pro 2.0|37367|
|feida.etool.rfwn0|FD射频控制器|19963|
|fnirsi.etool.40mpro|IR40智能测距仪|12215|
|fnirsi.etool.fn40m|FNIRSI 40m智能测距仪|8382|
|giot.etool.v1rfc|Gra射频控制器V1|23814|
|guixin.etool.v1|U-FAMILY 智能射频控制器PRO|38070|
|hhcc.bleflowerpot.v2|花花草草智能花盆|349|
|hoto.etool.finder|小猴智能激光测距仪|2530|
|hoto.etool.mf01|米家智能激光测距仪|3359|
|hoto.etool.plus01|小猴智能激光测距仪Plus|7890|
|ihealth.bp.bpm1|iHealth血压计|151|
|jdxc.pump.wysbm|Atman过滤泵|25467|
|lumi.86plug.v1|绿米86暗插|175|
|lumi.sensor_86sw1.v1|Aqara 无线开关（贴墙式单键版）|161|
|lumi.sensor_86sw2.v1|Aqara 无线开关（贴墙式双键版）|162|
|lumi.sensor_ir.v1|美的红外贴|68|
|mijia.insight.athena|智能感知|22589|
|mijia.ir.add|红外遥控器添加|66600|
|mijia.p_adapter.zb1|Zigbee设备|66165|
|niteli.pump.flwp1|白兰水泵|24796|
|niteli.pump.nlcf1|尼特利过滤桶|39012|
|niteli.pump.nlwp1|尼特利水泵|39013|
|njcuk.fitting.ad1204|酷态科10号超级电能充Ultra 充电器|26126|
|njcuk.fitting.c2c615|酷态科10号超级电能线Ultra（一拖二）|30415|
|rfgo.etool.rfgov1|RFGO遥控拷贝器（多门版）|39212|
|rfgo.etool.rfgov2|RFGO遥控拷贝器（单门版）|39215|
|senyou.etool.kzq01|SY射频控制器|33729|
|sfy.etool.sk002|索菲亚智能柜锁M1|25975|
|szks.etool.101|摩尔先生擦窗机器人|19183|
|szks.etool.103|M8摩尔先生擦窗机器人|24694|
|xgood.pump.yshsq|xgood 全自动换水泵|29043|
|xiaomi.demo.v1|小米开发板|38|
|xiaomi.demo.v2|小米开发板|40|
|xiaomi.phone_ir.t1|手机红外遥控器|117|
|xiaomi.phone_ir.v1|手机红外遥控器|70|
|yeelink.etool.wcb01|Yeelight T系列智能弱电箱面板|36086|
|yeeloc.etool.m09|易锁宝抽屉柜开关Pro|15599|
|zhiee.fitting.ad0|百将智能控制伴侣|32320|
|zinguo.etool.g6|峥果迎宾器|21823|
|zinguo.etool.sc01|智能温控器|8991|
|zinguo.etool.sc02p2|峥果多功能定时器|24263|
|zinguo.etool.sc03|峥果多段温控器|13612|
|zinguo.etool.sc03h4|峥果湿度控制器|26098|
|zinguo.etool.tk01|峥果太阳能热水器测控仪|20712|
|zinguo.pump.bk01|峥果水位控制器|28725|

### 出行车载

|model|name|pd_id|
|---|---|---:|
|913101.carseat.d1max|小海豚Ultra儿童安全座椅|27297|
|913101.carseat.d1pro|qborn小海豚儿童安全座椅|17106|
|candy.enstor.cp02s|CANDYSIGN 小电拼·充电管家（电源适配器）|84463|
|careco.evc.a07a01|小米汽车家用充电桩 7kW|25143|
|careco.evc.a07b01|小米汽车多功能家用充电桩 7kW|25144|
|careco.evc.d20a01|小米汽车直流家用充电桩 20kW|33734|
|careco.evc.power1|米家智能车载便携充放电枪|34323|
|chuangmi.wifi.v1|小米随身WIFI|125|
|gtmc.car.630d|铂智7|83641|
|ileja.hud.ccm|车萝卜智能HUD智炫版|69067|
|ileja.hud.ccms|车萝卜智能HUD智炫版Pro|70251|
|micar.car.kunlun|SKYNOMAD 小米澎程|20628|
|micar.car.ms11|Xiaomi SU7|12737|
|micar.car.ms11p|Xiaomi SU7 Ultra|20680|
|micar.car.ms12|Xiaomi 新一代SU7|22586|
|micar.car.mx11|Xiaomi YU7|19132|
|micar.car.mx11gt|Xiaomi YU7 GT|30491|
|micar.car.mx12|Xiaomi YU7|19136|
|midr.bike.x1|70迈智能电动车A1 Pro|68663|
|midr.cardvr.x200s|70迈云台记录仪|73896|
|midr.rv_mirror.m2|70迈智能后视镜青春版|796|
|midr.rv_mirror.m5|70迈智能行车助手|66361|
|migo.hud.ut0102|柚途抬头显示 G9 Pro|5164|
|navee1.scooter.t2208|NAVEE电动滑板车V40|11917|
|navee1.scooter.t2214|NAVEE电动滑板车S65C/D|11918|
|ninebot.balscooter.v1|迷你九号平衡车|108|
|njcuk.enstor.a11|CUKTECH 酷态科电能仓600|14595|
|njcuk.enstor.ap01|酷态科桌面充电站显示屏|31454|
|qicyc.bike.tdp02z|骑记电动助力自行车|1896|
|roidmi.btfm.m1|音乐蓝牙车充|289|
|roidmi.btfm.v1|车载蓝牙播放器|104|
|roidmi.carairpuri.pro|魔洁兔车载空气净化器P8S|653|
|roidmi.carairpuri.v1|米家车载空气净化器|332|
|runmi.suitcase.v1|90分智能金属旅行箱|149|
|sdt571.carseat.qzpro|两只兔子儿童安全座椅求知Pro|25833|
|uze.hud.jl101|九鹿抬头显示 GX|7309|
|xiaomi.carlight.cars1|智能底盘氛围灯|14782|
|xiaomi.carlight.cars3|智能底盘氛围灯|21299|
|xiaomi.carlight.cars4|智能底盘氛围灯|21300|
|zimi.powerbank.v1|ZMI智能移动电源|91|

### 办公学习

|model|name|pd_id|
|---|---|---:|
|17216.desk.lt001|乐班智能电动升降台|899|
|agkey.desk.k2|戟创AGKey天戟K2智能升降桌|29724|
|bkrobo.chair.bc03|贝氪智能托腰办公椅|4876|
|canon.printer.ij2|佳能双墨盒喷墨打印机|84025|
|canon.printer.ij4bk|佳能四色喷墨打印机|83994|
|hbada1.desk.s203u2|黑白调儿童智能学习桌 S2 Ultra|28719|
|hfzn.desk.hf01|H&F智能升降桌|18164|
|jiqid.sxb.v1|小米米家液晶小黑板-存储版|4056|
|jstar.desk.jcb36|AIDESK|12527|
|kukeli.desk.cxxz01|酷可立电动学习桌|8905|
|miuni.desk.mztz|吉木江南智能升降桌|26348|
|mns168.desk.nssjz|耐实智能升降桌（WiFi）|29040|
|morlin.desk.mdszz|美迪丝智能升降桌（WiFi）|24772|
|nineam.desk.hoo01|9am智能升降桌|5635|
|nineam.desk.hoo021|9am L系列升降桌|6472|
|nineam.desk.t06|9am Dora智能升降桌|16044|
|nineam.desk.u2t|9am Raven X 智能电竞桌|21095|
|nineam.desk.u5|9am Viva 智能学习桌|21632|
|qushui.desk.sjz001|8H 智能升降桌|22289|
|qushui.desk.sjz02|8H 智能升降桌D系列|22752|
|univer.desk.t0|游戏家升降桌|8079|
|wnzq.desk.wnzjz|为诺智能升降桌（WiFi）|28370|
|wzt.desk.h100|AOKE智能升降桌|14038|
|wzt.desk.h101|AIMIZO爱美卓智能升降桌|15181|
|wzt.desk.h102|ULOVEHOME尤爱智能升降桌|15182|
|xlang.desk.djz|NOC LOC智能电竞升降桌|7845|
|xlang.desk.nlocv1|NOC LOC智能电动儿童学习桌|4236|
|xlang.desk.vlocv2|NOC LOC 智能办公升降桌|5172|

### 卫浴

|model|name|pd_id|
|---|---|---:|
|090615.bhf_light.ptxyb|PTX 智能浴霸A1|9494|
|090615.wafa.f11026|民洁鲸智面盆龙头|18105|
|445.shower.lyq01|大白智联恒温淋浴花洒 P1|38287|
|445.toilet.cnlzmt|大白超能离子智能马桶梦月银 AIOT版|5863|
|445.toilet.mt01|大白智能马桶|26300|
|445.toilet.mt02|大白智能马桶 N8 奔腾Plus版|31845|
|445.toilet.mt03|大白轻智能马桶 N8 奔腾Plus版|35736|
|445.toilet.mt04|大白智能马桶 S3 奔腾Plus版|35737|
|445.toilet.mt06|大白轻智能马桶 N9 奔腾Plus版|35739|
|445.toilet.mt09|大白轻智能马桶 N18Q 奔腾Plus版|39274|
|445.toilet.mt10|大白轻智能马桶 N20Q 奔腾智联版|39920|
|445.toilet.tjznmt|大白sky I 天境智能马桶 空净IoT版|7700|
|445.toilet.xmt015|大白双擎增压智能马桶AIOT版|7036|
|445.tow_w.mjj1|大白AIOT毛巾架|31541|
|aden.waterheater.ash200|VINO空气能热水器200L|14161|
|aobrn.bhf_light.1|FUNTI浴霸|34100|
|aosi.toilet.a9999|英米智能马桶盖-M68|23710|
|aosi.toilet.m|英米智能马桶-M|27512|
|aupu.bhf_light.360ap|奥普空气管家Q360A-Pro|11157|
|aupu.bhf_light.360pro|奥普浴霸Q360C-Pro|15327|
|aupu.bhf_light.360t3s|奥普浴霸Q360T3S|18545|
|aupu.bhf_light.360x3|奥普浴霸Q360X3|18547|
|aupu.bhf_light.360xp|奥普空气管家浴霸Q360X-Pro|11158|
|aupu.bhf_light.a3e2|AUPU奥普浴霸Q360A3-Evo|24145|
|aupu.bhf_light.a3pro2|奥普浴霸Q360A3-Air|22926|
|aupu.bhf_light.a3sp2|奥普热能环系列水氧浴霸Q360A3S-Pro+|24143|
|aupu.bhf_light.a3spro|奥普浴霸Q360A3S-Pro|18544|
|aupu.bhf_light.a3ss|奥普热能环系列人感浴霸Q360A3S-S|28159|
|aupu.bhf_light.dl05a|奥普浴霸DL05A|24841|
|aupu.bhf_light.dl06a|奥普浴霸DL06A|25455|
|aupu.bhf_light.e371|奥普浴霸E371M|16509|
|aupu.bhf_light.e371my|奥普浴霸E371M-Y|21858|
|aupu.bhf_light.e372|奥普浴霸E372M|16546|
|aupu.bhf_light.e372my|奥普浴霸E372M-Y|21859|
|aupu.bhf_light.f1pro1|奥普浴霸F1-Pro|14783|
|aupu.bhf_light.fxpro|奥普浴霸FX-Pro|14784|
|aupu.bhf_light.fy|奥普奥芯恒温线性浴霸 FY|27854|
|aupu.bhf_light.fypro|奥普奥芯双氧线性浴霸 FY-Pro+|27853|
|aupu.bhf_light.g10|奥普浴霸G10|27859|
|aupu.bhf_light.gl19p|奥普线性浴霸GL19-Pro+|33942|
|aupu.bhf_light.gl21p|奥普线性浴霸GL21-Pro+|33463|
|aupu.bhf_light.ha01md|奥普浴霸HA01MD|19173|
|aupu.bhf_light.jqsair|奥普Smart系列人感浴霸JQS-Air|31304|
|aupu.bhf_light.l1b|奥普浴霸L1B|20307|
|aupu.bhf_light.l1b2|AUPU奥普线性浴霸L1B|24148|
|aupu.bhf_light.l1bs|奥普浴霸L1BS|20321|
|aupu.bhf_light.l1bs2|AUPU奥普线性浴霸L1BS|24147|
|aupu.bhf_light.l2air|奥普线性浴霸 L2A-Air|27856|
|aupu.bhf_light.l3b|奥普线性浴霸 L3B|27855|
|aupu.bhf_light.l3bpro|奥普线性浴霸L3B-Pro+|27762|
|aupu.bhf_light.l3bs|奥普线性浴霸 L3B-S|28506|
|aupu.bhf_light.mr005|奥普美容舱浴霸MR005|27704|
|aupu.bhf_light.mr009|奥普美容舱浴霸MR009M|27705|
|aupu.bhf_light.n80|奥普空气管家浴霸-N80Pro|7624|
|aupu.bhf_light.n80ss|奥普浴霸N80S|15063|
|aupu.bhf_light.na01dp|奥普浴霸NA01-Pro|19113|
|aupu.bhf_light.p3328e|奥普浴霸-奥芯|8549|
|aupu.bhf_light.q360a3|奥普浴霸Q360A3|17592|
|aupu.bhf_light.q360c|奥普浴霸Q360C|14084|
|aupu.bhf_light.q360g3|奥普浴霸Q360G3|21639|
|aupu.bhf_light.q360sp|奥普空气管家浴霸Q360S-Pro|10392|
|aupu.bhf_light.qa32|AUPU奥普浴霸Q360A3|22846|
|aupu.bhf_light.qa3evo|奥普浴霸Q360A3-Evo|18381|
|aupu.bhf_light.qa3pro|奥普浴霸Q360A3-Pro|18382|
|aupu.bhf_light.qa3s|奥普浴霸Q360A3S|18543|
|aupu.bhf_light.s01m|奥普浴霸S01M|19112|
|aupu.bhf_light.s01m2|AUPU奥普浴霸S01M|22894|
|aupu.bhf_light.s01md|奥普浴霸S01MD|19111|
|aupu.bhf_light.s01md2|AUPU奥普浴霸S01MD|22895|
|aupu.bhf_light.s10m|奥普浴霸S10M|12927|
|aupu.bhf_light.s10m2|AUPU奥普浴霸S10M|22806|
|aupu.bhf_light.s118m1|奥普浴霸S118M|10874|
|aupu.bhf_light.s11m|奥普浴霸S11M|12928|
|aupu.bhf_light.s11m2|AUPU奥普浴霸S11M|22807|
|aupu.bhf_light.s2|奥普Smart浴霸S2|26127|
|aupu.bhf_light.s2air|奥普Smart浴霸S2-Air|26115|
|aupu.bhf_light.s368m|奥普浴霸S368M|6077|
|aupu.bhf_light.s368m2|奥普浴霸S368M|13218|
|aupu.bhf_light.s368m3|AUPU奥普浴霸S368M|22805|
|aupu.bhf_light.s608m|奥普浴霸S608M|16983|
|aupu.bhf_light.s608m2|AUPU奥普浴霸S608M|22808|
|aupu.bhf_light.s618m1|奥普浴霸S618M|12901|
|aupu.bhf_light.s618m2|AUPU奥普浴霸S618M|22804|
|aupu.bhf_light.s628m|奥普浴霸S628M|12902|
|aupu.bhf_light.s628m2|AUPU奥普浴霸S628M|22803|
|aupu.bhf_light.se2|奥普热浪系列恒温浴霸SE2|27522|
|aupu.bhf_light.se2air|奥普热浪系列恒温浴霸SE2-Air|37533|
|aupu.bhf_light.t01m|奥普浴霸G1|25454|
|aupu.bhf_light.t01md|奥普浴霸G1-Air|25453|
|aupu.bhf_light.t3sp2|奥普浴霸Q360T3S-Air|24141|
|aupu.bhf_light.t3spro|奥普浴霸Q360T3S-Pro|18546|
|aupu.bhf_light.x3pro|奥普浴霸Q360X3-Pro|18548|
|aupu.bhf_light.x3pro2|奥普浴霸Q360X3-Air|24139|
|awl.tow_w.awl1|EVANLEY电热毛巾架|30398|
|axent.tow_w.a804|AXENT和煦电热毛巾架|7588|
|babai.bhf_light.kmdm01|Comotomo智能浴霸|7223|
|babai.bhf_light.mk885|米科智能浴霸|5902|
|babai.bhf_light.tyhot|天语智能浴霸|13150|
|bardis.bhf_light.yb1590|巴迪斯智能浴霸BDS-JK-AI·1590-FHAZ-VC|37343|
|bardis.bhf_light.yb3060|巴迪斯智能浴霸BDS-WJ-AI·3060-FHAZ|37310|
|becbas.wafa.f05|贝克巴斯超级感应龙头F05PRO|20601|
|bull.bhf_light.gy29|公牛恒温浴霸Y29|32731|
|bull.bhf_light.yub01|公牛浴霸Y79A|34339|
|bull.bhf_light.yub02|公牛浴霸Y77A|35300|
|bull.bhf_light.yub03|公牛浴霸Y72A|35587|
|cchome.tow_w.wyj001|倍增智能卫浴架|70293|
|cdn.bhf_light.zjd606|西顿多功能智能浴霸|6350|
|cdn.bhf_light.znyb|西顿智能浴霸|30475|
|chnt.bhf_light.yb01|正泰石墨烯智能浴霸|39096|
|cozy.toilet.jittgo|JITTGO智能马桶一体机|14204|
|cozy.toilet.noeo|NOEO智能马桶|14480|
|cozy.toilet.s1|光翼X1智能马桶|12965|
|csykj.tow_w.xymjw|芯毅智能毛巾架|25911|
|csykj.tow_w.ykmjw|仪克电热毛巾架|33119|
|cycle.waterheater.d1|赛科拉智能热水循环器D1|3396|
|dawn.toilet.02|ZBZ智能马桶|16214|
|dawn.toilet.808|科恩达一体式智能马桶808|14677|
|dawn.toilet.max808|智能坐便器MAX|17028|
|dfl888.toilet.toilet|智能马桶|12428|
|dilan.bhf_light.hydlv2|DL浴霸|38251|
|disen.waterheater.slm6|小松鼠壁挂炉|6745|
|dlb.bhf_light.gx1|德莱宝线型浴霸 极线GX1|7815|
|dlx.bhf_light.dlxyb|德力西智能浴霸|30927|
|dmzz.bhf_light.02|容声智能浴霸V1|23304|
|dmzz.bhf_light.dm01|鼎美智能浴霸V1|21900|
|ds2023.bhf_light.ds1|DS顶上智能浴霸|31450|
|dsmile.bhf_light.001|顶善美智能浴霸C7L|19655|
|dz888.toilet.m|小鸿智能马桶一体机|14172|
|eafly.waterheater.17sk|鹰游智能零冷水系统 17SK|29358|
|eafly.waterheater.qb001|鹰游智能零冷水系统|28121|
|fbis.toilet.std01|摩恩弗里斯安心座智能坐便器 Pro|27264|
|fbis.toilet.std02|摩恩弗里斯安心座智能坐便器|32642|
|fbis.tow_w.strd01|摩恩卢米电热毛巾架单片装|24358|
|fbis.tow_w.strd02|摩恩卢米电热毛巾架两片装|33297|
|fbis.tow_w.strd03|摩恩卢米电热毛巾架三片装|33298|
|fdjm99.bhf_light.fdjm03|简美智能浴霸Plus|32685|
|feid.bhf_light.yz001|飞雕悦智智能浴霸|35884|
|filos.tow_w.afd06|艾芬达毛巾架GD18-A|9861|
|filos.tow_w.x|奥享毛巾架|9646|
|fojee.toilet.fjzn01|福联智能马桶|16479|
|fsilon.bhf_light.001|法狮龙智能浴霸XN-F120-2A|22292|
|fsilon.bhf_light.002|法狮龙智能浴霸FDN26-S13|24497|
|fsilon.bhf_light.003|法狮龙智能浴霸YN-E520-1A|25008|
|fsilon.bhf_light.kte80a|法狮龙智能冷暖浴霸KT-E80-1A|32479|
|fsilon.bhf_light.s18|法狮龙智能浴霸FDN26-S18|29311|
|fsilon.bhf_light.xn1a|法狮龙智能浴霸XN-E159-1A|30212|
|fssd.tow_w.kb01|卡贝电热毛巾架|15399|
|fssd.tow_w.lc20a9|智慧电热毛巾架|12309|
|ftd.bhf_light.bthmsh|BSH智能浴霸V2(MESH)|25128|
|ftd.bhf_light.testmd|智能浴霸(WIFI版)|14577|
|futuo1.tow_w.s2|赛莱诺电热毛巾架|30578|
|giot.bhf_light.auxbh|奥克斯浴霸|20873|
|giot.bhf_light.jpbm|箭牌浴霸|12637|
|giot.bhf_light.lbhw1|DL线性浴霸（WiFi）|19481|
|giot.bhf_light.sjbm|四季沐歌浴霸|12636|
|giot.bhf_light.v1ibhw|V1智能浴霸（WiFi）|15902|
|giot.tow_w.v1itrw|V1智能毛巾架（WiFi）|17023|
|gmn.bhf_light.yb1|情景智能浴霸|3467|
|gtop.bhf_light.b1|智能情景浴霸|14686|
|haierj.bhf_light.hjc1|Haier智能浴霸HJC-1|31675|
|haierj.bhf_light.sr5m|Haier智能浴霸SR5M|31666|
|hegii.toilet.he110a|恒洁智能马桶|28240|
|hjk666.toilet.h1|小康智能马桶|14189|
|honyar.bhf_light.55w|iHouse智能风暖浴霸FZ系列|30417|
|honyar.bhf_light.f|iHouse智能风暖浴霸F系列|31588|
|honyar.bhf_light.m10w|iHouse智能浴霸M系列|36227|
|honyar.bhf_light.yb51w|iHouse智能感知横出风浴霸FZHZ33-51W|27699|
|honyar.bhf_light.yb54w|iHouse智能感知横摆风浴霸FZHZ33-54W|27701|
|horow.toilet.s10|希箭大冲力智能马桶S10|72378|
|horow.toilet.s10l|希箭大冲力智能马桶S10L|76084|
|horow.toilet.s4|希箭大冲力智能马桶|70171|
|horow.toilet.s4p|希箭大冲力智能马桶S4|74169|
|hsgczx.toilet.ctv1|智能健康马桶盖|3470|
|huayi.bhf_light.libra|慧作天秤星浴霸Pro|1704|
|huida.toilet.et65q|惠达智能连体坐便器HDET65-Q Pro|5410|
|hzft.waterheater.mx16t1|方太智能热水器|81580|
|ijomoo.bhf_light.jd071|九牧智能浴霸-JD071|8811|
|ijomoo.toilet.i90|九牧智能马桶 i90|4401|
|ijomoo.toilet.zs320|九牧智能马桶-ZS320T|68918|
|ijomoo.tow_w.z300x|九牧电热毛巾架|26955|
|iot.tow_w.jd015|智能电热毛巾架|10924|
|jcy.tow_w.sy01|六麦电热毛巾架|33027|
|jddm.bhf_light.yb0a01|金盾顶美智能浴霸|10562|
|jdjz.tow_w.v1|京东京造智能毛巾架 JZ-M10D|35602|
|jxdh.bhf_light.dh001|智芯浴霸1号Pro|14259|
|jxzc.bhf_light.fzfvyb|FZFV智能浴霸|33127|
|jyf.tow_w.jyf01|JYF智能电热毛巾架|24863|
|jyf.tow_w.mj01|多功能除菌烘干机|11292|
|jyf.tow_w.ts03|烘干毛巾架|9109|
|kadiyo.tow_w.kdomj|卡迪欧电热毛巾架（WiFi）|29100|
|kddq.bhf_light.1|巴洛斯顿智能浴霸|32481|
|kddq.bhf_light.2|巴洛斯顿AI人感浴霸|34870|
|kind8.bhf_light.002|今顶智能浴霸AI|29025|
|kind8.bhf_light.m|今顶智能浴霸M|25928|
|koey.bhf_light.yb0a01|KOEY智能护眼浴霸|17083|
|kpcrkj.tow_w.sy|YONGEER 智能毛巾架 E|29719|
|leishi.bhf_light.ls109|雷士智能浴霸N1|4211|
|leishi.bhf_light.lsdcyb|雷士智能全色域浴霸|31517|
|leishi.bhf_light.lsxxyb|雷士智能浴霸C2|31471|
|leishi.bhf_light.lsyb01|雷士智能浴霸V2|6824|
|leishi.bhf_light.lsyb02|雷士智能浴霸N2|10865|
|leishi.bhf_light.lsyb03|雷士智能浴霸N3|11196|
|leishi.bhf_light.lsyb04|雷士智能浴霸N4|13130|
|leishi.bhf_light.lsybc1|雷士智能浴霸C1|22907|
|leishi.bhf_light.pro1|雷士智能浴霸pro|13074|
|leishi.bhf_light.rnhyb|雷士热能环智能浴霸|33596|
|leishi.bhf_light.smart|雷士智能感应浴霸|29798|
|leishi.bhf_light.smart2|雷士AI智能浴霸|34689|
|leishi.bhf_light.smart4|雷士AI智能滑盖浴霸|35599|
|leishi.bhf_light.tyyb|雷士智能浴霸V3|17394|
|leishi.bhf_light.yb1|雷士智能AI人感浴霸|37022|
|leishi.bhf_light.ybjck|雷士智能浴霸V|16491|
|leishi.bhf_light.yuba02|雷士智能浴霸|2737|
|lhz.bhf_light.hy274|罗格朗智能浴霸 HY274|34177|
|lipro.bhf_light.e3u1|lipro柔风浴霸E2 Pro|19154|
|lipro.bhf_light.e5u1|lipro柔风浴霸E2|29195|
|lunsun.bhf_light.n8703|名族智能浴霸MZ|21793|
|lxzn.bhf_light.01|LTP智能浴霸L1|21355|
|lxzn.bhf_light.ben|LTP智能浴霸控制Pro|21587|
|macro.waterheater.jsq01|万家乐家用冷凝式供热水燃气快速热水器|82755|
|macro.waterheater.w9|万家乐储水式电热水器|83761|
|mcosu.bhf_light.pipam1|PIPA 智能浴霸M1|7612|
|mell88.bhf_light.001|美尔凯特AI除味智能浴霸|36797|
|miabs.toilet.614|维恩智能马桶|32824|
|miir.waterheater.ir01|热水器遥控|65718|
|mike.bhf_light.2|智能浴霸Pro（AI版）YB-007|11390|
|mxc.toilet.toilet|智能马桶控制器|19273|
|mxl.tow_w.dmg45|木希林智能毛巾架A8|39272|
|mxl.tow_w.mjj001|大拇哥智能电热毛巾架A9|16670|
|mxl.tow_w.mjj002|大拇哥智能电热毛巾架A6|16783|
|nanmg.toilet.601|智能马桶一体机601|14498|
|nanmg.toilet.dan|松而智能马桶一体机未来蛋|24176|
|noritz.waterheater.16d4|能率燃气热水器|82787|
|opple.bhf_light.acmoto|欧普智能浴霸 Mode A|2557|
|opple.bhf_light.ct88|欧普智能浴霸 Mode C|9260|
|opple.bhf_light.ct88b|欧普智能浴霸 Mode F|12739|
|opple.bhf_light.dcmoto|欧普智能浴霸 Mode B|3032|
|opple.bhf_light.fhbath|欧普智能浴霸 BPF12i|7762|
|opple.bhf_light.fx88a|欧普智能浴霸 Mode D|9276|
|opple.bhf_light.mkc3|欧普智能浴霸 Mode E|11049|
|opple.bhf_light.mkcj|欧普智能浴霸 Mode J|19278|
|opple.bhf_light.sdd221|欧普智能浴霸  Mode K|30659|
|opple.bhf_light.wlyb|欧普智能浴霸 Mode G|12822|
|opple.bhf_light.xgb26|欧普智能浴霸 Mode L|34278|
|oumei.bhf_light.om001|M多功能浴霸Z|38652|
|our.bhf_light.df001|奥华取暖器|12555|
|our.bhf_light.pro|奥华智能浴霸pro|31585|
|our.bhf_light.pro2|奥华智能浴霸pro+|38007|
|ouso.tow_w.mjj01|欧素智能电热毛巾架|33808|
|ouso.tow_w.mjj02|欧素外置智能电热毛巾架|36330|
|ows.tow_w.mjj20a|欧伟士NEX毛巾架|4579|
|ows.tow_w.mjjs1|欧伟士S1毛巾架|7456|
|ows.tow_w.mjjxs|欧伟士智能电热毛巾架XS|12211|
|ows.tow_w.nexpro|欧伟士电热毛巾架NEXpro|17600|
|ows.tow_w.s|欧伟士电热毛巾架S·Pro|21884|
|ows.tow_w.xp|欧伟士电热毛巾架OWS-X|22360|
|ows.towel_w.mj1x0|欧伟士智能电热毛巾架|67363|
|pak.bhf_light.pak11|三雄智能浴霸|7937|
|pak.bhf_light.pak16|三雄极光Pak智能浴霸|18289|
|pesgd.bhf_light.rb26|松下浴霸FV-RB26UL1|33572|
|pesgd.bhf_light.rb26dl|松下浴霸FV-RB26DL1|34235|
|pesgd.bhf_light.rb29dl|松下浴霸FV-RB29DL1|34236|
|pesgd.bhf_light.w|松下浴霸FV-RB29NL1|35710|
|phnix.waterheater.sf|芬尼空气能热水器|1207|
|pogor.bhf_light.k1p2ul|品格智尊·极暖浴霸K1Pro Ⅱ Ultra|38074|
|pogor.bhf_light.k1pro2|品格智尊·极暖浴霸K1Pro Ⅱ|34947|
|qike.bhf_light.qk201801|智慧浴霸(基础版)|66195|
|qiqi.bhf_light.qbot23|宇邦智能浴霸开关|14947|
|qjiang.bhf_light.a1|QM智能浴霸AI|21962|
|qjiang.bhf_light.gs001|GS智能晾衣浴霸|26813|
|qjiang.tow_w.001|QM智能毛巾架|23701|
|raile.bhf_light.sdjyby|智能线型浴霸|18142|
|resmo.shower.shower|瑞摩N1三功能智能淋浴器|32811|
|rinnai.waterheater.e42g|林内燃气热水器|81200|
|roome.bhf_light.1036f|箭牌智能浴霸 X1|68814|
|roome.bhf_light.1037fx|箭牌智能浴霸 X2|69416|
|roome.bhf_light.yf6002|M-YF6002智能浴霸|67115|
|roome.bhf_light.yf6004|M-YF6002A智能浴霸|68309|
|roome.bhf_light.yf6005|M-YF6003智能浴霸|68716|
|scc.bhf_light.yb1|西蒙智能浴霸|34051|
|sfl.bhf_light.fslyb|FSL智能浴霸|31621|
|sfl.bhf_light.fslyb2|FSL智能人感浴霸|38766|
|sfl.bhf_light.ybe20|FSL智曜浴霸|38758|
|sharnd.tow_w.rda01|想的智能电热毛巾架|22901|
|sinl.tow_w.s1|智能触屏毛巾烘干机|9451|
|smith.waterheater.cxea1|佳尼特电热水器CXE-A1|66988|
|smith.waterheater.cxeb1|佳尼特电热水器CXE-60B1|66987|
|smith.waterheater.x1|佳尼特电热水器CTE-X1|5109|
|supor8.bhf_light.spryb|SUPOR浴霸|32880|
|supor8.bhf_light.spryb2|SUPOR风暖浴霸|36055|
|supor8.bhf_light.spryb3|SUPOR智能浴霸|36443|
|sursca.bhf_light.yb1|SURSCA舒世嘉智能浴霸|32247|
|syzn01.tow_w.sy119|智能烘干毛巾架|18584|
|tcll.bhf_light.yb01|TCL华照浴霸|12326|
|tcll.bhf_light.yb02|TCL智能浴霸风华5Pro|15274|
|tcll.bhf_light.yb03|TCL智能浴霸S2Pro|21171|
|tinymu.toilet.ailid|小沐智能马桶盖AI版|883|
|tinymu.toilet.wmt15|小沐智能马桶盖 旗舰版（V型）|5017|
|tinymu.toiletlid.v1|小沐智能马桶盖|519|
|tm666.toilet.t1|小它智能马桶|18277|
|topwit.bhf_light.htw02|智能浴霸|9925|
|topwit.bhf_light.rz01|智能浴霸开关|5962|
|topwit.bhf_light.rzw76|IWN小铃铛智能浴霸开关|26045|
|topwit.bhf_light.yzw08|IWN小铃铛六位单零火兼容浴霸开关|30680|
|uvfive.tow_w.berry|FIVE智能热毛巾机|5738|
|uwize.bhf_light.yzw01|UWIZE优智者六位单零火兼容浴霸开关|32567|
|uxkeji.bhf_light.ux47|阳光智能浴霸|10020|
|vanco.toilet.max1|Vancoco智能马桶一体机星月MAX|11108|
|vanco.toilet.pro1|Vancoco智能马桶一体机星月Pro|6139|
|vatti.waterheater.12581|华帝燃气热水器|83918|
|vatti.waterheater.dj10|华帝电热水器DJ10|14692|
|vatti.waterheater.ds9|华帝电热水器DS9|14691|
|vatti.waterheater.yp07i|华帝电热水器DJ9|12715|
|viomi.bhf_light.v1|云米互联网浴霸|66122|
|viomi.bhf_light.v10|云米互联网直流变频浴霸S1 摆风版|4544|
|viomi.bhf_light.v3|云米互联网浴霸Pro（风暖触控版）|67972|
|viomi.bhf_light.v4|云米互联网浴霸A1|69397|
|viomi.bhf_light.v6|云米互联网浴霸 风暖双核版|71369|
|viomi.bhf_light.v8|云米互联网直流变频浴霸S1|4364|
|viomi.bhf_light.v9|云米互联网浴霸 风暖摆风版|4542|
|viomi.toilet.m05|云米智能马桶Nano2 Max 智联版|8883|
|viomi.toilet.m06|云米AI健康检测马桶Air|6142|
|viomi.toilet.m10|云米智能马桶 小鲸鱼 2 Pro|22145|
|viomi.waterheater.e1|云米互联网电热水器1A（60L）|65820|
|viomi.waterheater.e13|云米互联网免更换镁棒电热水器 50L|67746|
|viomi.waterheater.e14|云米互联网免更换镁棒电热水器 60L|67745|
|viomi.waterheater.e15|云米互联网免更换镁棒电热水器 80L|67744|
|viomi.waterheater.e16|云米互联网电热水器C1（50L）|68941|
|viomi.waterheater.e17|云米互联网电热水器C1（60L）|68942|
|viomi.waterheater.e19|云米互联网电热水器VEW5015|70247|
|viomi.waterheater.e20|云米互联网电热水器VEW6015|70248|
|viomi.waterheater.e21|云米互联网电热水器VEW5016|70249|
|viomi.waterheater.e22|云米互联网电热水器VEW6016|70250|
|viomi.waterheater.e24|云米互联网电热水器VEW5018|71792|
|viomi.waterheater.e25|云米互联网电热水器VEW6018|71793|
|viomi.waterheater.e26|云米互联网电热水器VEW5019|71794|
|viomi.waterheater.e27|云米互联网电热水器VEW6019|71795|
|viomi.waterheater.e28|云米AI电热水器VEW5020|71796|
|viomi.waterheater.e29|云米AI电热水器VEW6020|71797|
|viomi.waterheater.e3|云米互联网电热水器Air（60L双胆语音）|66187|
|viomi.waterheater.e33|云米AI电热水器VEW6022|5150|
|viomi.waterheater.e38|云米AI电热水器小蓝调|8935|
|viomi.waterheater.e4|云米互联网电热水器50L（优享版）|66188|
|viomi.waterheater.e42|蓝调智能电热水器|9275|
|viomi.waterheater.e44|云米AI电热水器 Air 双胆优享版|10487|
|viomi.waterheater.e45|云米AI电热水器 Super|10488|
|viomi.waterheater.e47|云米AI电热水器Smart 2|12730|
|viomi.waterheater.e48|云米AI电热水器Super 2 Pro|13338|
|viomi.waterheater.e49|云米AI电热水器 Smart E|17022|
|viomi.waterheater.e50|云米AI电热水器 Super 3|21622|
|viomi.waterheater.e7|云米互联网电热水器Air（60L 双胆优享版）|66606|
|viomi.waterheater.e8|云米互联网电热水器Air（60L双胆智享版）|66605|
|viomi.waterheater.u1|云米互联网燃气热水器1A（13L）|65816|
|viomi.waterheater.u10|云米互联网燃气热水器Zero（13L零冷水）|66512|
|viomi.waterheater.u11|云米互联网燃气热水器Zero（13L零冷水 优享版）|66511|
|viomi.waterheater.u12|云米互联网燃气热水器Zero（16L零冷水 优享版）|66510|
|viomi.waterheater.u15|云米互联网燃气热水器Zero（12L零冷水）|66937|
|viomi.waterheater.u16|云米互联网燃气热水器1C 16L|67407|
|viomi.waterheater.u17|云米互联网燃气热水器S1|68752|
|viomi.waterheater.u18|云米互联网燃气热水器S1|68753|
|viomi.waterheater.u19|云米互联网燃气热水器（12L优享版）（液化气）|68768|
|viomi.waterheater.u22|云米互联网燃气热水器C1 13L|69553|
|viomi.waterheater.u23|云米互联网燃气热水器C1 16L|69554|
|viomi.waterheater.u24|云米互联网燃气热水器A1 13L|69555|
|viomi.waterheater.u25|云米互联网燃气热水器A1 16L|69556|
|viomi.waterheater.u26|云米互联网燃气热水器Zero S1 (13L 零冷水)|69803|
|viomi.waterheater.u27|云米互联网燃气热水器Zero S1 (16L 零冷水)|69804|
|viomi.waterheater.u29|云米互联网燃气热水器Mate Pro 13L|70116|
|viomi.waterheater.u3|云米互联网燃气热水器1C（13L）|66046|
|viomi.waterheater.u30|云米互联网燃气热水器Mate Pro 16L|70117|
|viomi.waterheater.u31|云米互联网燃气热水器Mate 13L|70375|
|viomi.waterheater.u32|云米互联网燃气热水器Mate 16L|70376|
|viomi.waterheater.u33|云米互联网燃气热水器VGW1615 16L|70408|
|viomi.waterheater.u34|云米互联网燃气热水器VGW1815 18L|70409|
|viomi.waterheater.u36|coKiing AI燃气热水器 VGW1616 16L|70945|
|viomi.waterheater.u37|coKiing AI燃气热水器 VGW1816 18L|70946|
|viomi.waterheater.u38|云米互联网燃气热水器VGW1817 18L|71020|
|viomi.waterheater.u39|云米互联网燃气热水器VGW1617 16L|71021|
|viomi.waterheater.u4|云米互联网燃气热水器1A （13L）|66107|
|viomi.waterheater.u40|云米互联网燃气热水器VGW1314|71327|
|viomi.waterheater.u41|云米互联网燃气热水器VGW1614|71328|
|viomi.waterheater.u42|云米互联网燃气热水器VGW1318 13L|71408|
|viomi.waterheater.u43|云米互联网燃气热水器VGW1618 16L|71409|
|viomi.waterheater.u48|云米互联网燃气热水器VGW1621 16L|4725|
|viomi.waterheater.u49|云米互联网燃气热水器VGW1821 18L|4726|
|viomi.waterheater.u50|云米互联网燃气热水器VGW1622 16L|4727|
|viomi.waterheater.u51|云米互联网燃气热水器VGW1822 18L|4728|
|viomi.waterheater.u52|云米AI燃气热水器VGW1623 16L|5775|
|viomi.waterheater.u53|云米AI燃气热水器VGW1823 18L|5776|
|viomi.waterheater.u55|云米AI燃气热水器 小蓝调|8756|
|viomi.waterheater.u57|云米AI零冷水燃气热水器Super|8758|
|viomi.waterheater.u6|云米互联网燃气热水器16L(优享版)|66184|
|viomi.waterheater.u62|云米AI零冷水燃气热水器 Super 2 Max|9087|
|viomi.waterheater.u63|云米AI燃气热水器Zero2 C1|9321|
|viomi.waterheater.u65|云米AI零冷水燃气热水器 Super 2 Max|11605|
|viomi.waterheater.u66|云米AI零冷水燃气热水器Super|11606|
|viomi.waterheater.u67|云米AI燃气热水器Master 3 Pro|12341|
|viomi.waterheater.u68|云米AI燃气热水器Smart|12418|
|viomi.waterheater.u69|云米AI燃气热水器 Smart Pro|12553|
|viomi.waterheater.u7|云米互联网燃气热水器Zero（16L零冷水）|66185|
|viomi.waterheater.u70|云米AI燃气热水器 Super Pro|13279|
|viomi.waterheater.u72|云米AI燃气热水器 Super 2|18014|
|viomi.waterheater.u73|云米AI燃气热水器 Super 2 Pro|18015|
|viomi.waterheater.u8|云米互联网燃气热水器Zero（18L 零冷水）|66186|
|wanhe.waterheater.2232|万和燃气热水器|81556|
|wanhe.waterheater.a6pro|万和电热水器出水断电款|82207|
|wanhe.waterheater.q2|万和电热水器智能款|82253|
|wanhe.waterheater.r6t|万和燃气热水器恒温款2.0|82795|
|wanhe.waterheater.s5|万和热水器S5|3500|
|wanhe.waterheater.test|万和燃气热水器_零冷水款|82206|
|wzcb.tow_w.cobbe1|cobbe智能毛巾架|32077|
|xckj.waterheater.int01|圈厨超薄互联网电热水器50L|68203|
|xckj.waterheater.int02|圈厨超薄互联网电热水器60L|69123|
|xinzhi.bhf_light.zhyb01|智慧云浴霸|70922|
|xjx.toilet.pro|小鲸洗智能坐便盖Pro版|65782|
|xjx.toilet.pure|小鲸洗一体式智能马桶Pure|68660|
|xjx.toilet.relax|小鲸洗一体式智能马桶Relax|68661|
|xjx.toilet.relaxp|小鲸洗一体式智能马桶 Relax plus|75430|
|xjx.toilet.zero|小鲸洗智能一体式马桶坐便器ZERO|67686|
|xox.toilet.ts|云马智控智能马桶Pro版|15084|
|xt1234.tow_w.e1|恩柏斯毛巾架E1|30884|
|xunzhi.bhf_light.01|浴霸智能遥控开关|15832|
|xunzhi.bhf_light.02|数智鸟智能浴霸开关|30640|
|yeelink.bhf_light.v5|米家智能浴霸Pro|1631|
|yeelink.bhf_light.v6|Yeelight 智能浴霸 S20|3261|
|yeelink.bhf_light.znyb1|Yeelight 智能浴霸|29615|
|yj1226.waterheater.js01|今闪零冷水热水循环器|32586|
|yooeca.tow_w.mj04|智能毛巾烘干机|9433|
|yopins.tow_w.mimj01|YOPINS智能毛巾机|8375|
|youpon.bhf_light.x7|友邦智能浴霸X7系列|19617|
|youpon.bhf_light.yb0a01|友邦智能浴霸DZ系列|4973|
|yunmi.waterheater.e51|云米AI双胆电热水器 蓝调2|25993|
|yunmi.waterheater.u74|云米AI恒温燃气热水器 Master|24941|
|yunmi.waterheater.u75|云米AI燃气热水器蓝调2|26533|
|yunmi.waterheater.u77|云米AI零冷水燃气热水器 Master E|28531|
|yunmi.waterheater.u78|云米AI燃气热水器 蓝调2 Pro|29528|
|yunmi.waterheater.u79|云米蓝调2 Pro燃气热水器静音增压16L|29630|
|yunmi.waterheater.u80|云米大师燃气热水器13L|29722|
|yunmi.waterheater.u81|云米冠军燃气热水器16L|32978|
|yunmi.waterheater.u82|云米冠军Pro燃气热水器16L|32979|
|yunmi.waterheater.u83|云米大师Pro燃气热水器16L|33601|
|yunmi.waterheater.u84|云米鲲鹏燃气热水器16L|33602|
|yywq.toilet.wqzn01|云奇智控智能马桶AIR版|15540|
|zhimi.toilet.pa5|智米智能马桶一体机2PRO|12548|
|zjcq.bhf_light.01|楚楚线性浴霸37Z|21339|

### 厨房电器

|model|name|pd_id|
|---|---|---:|
|babai.ven_fan.tycold|天语智能凉霸|13152|
|bdx.i_stove.a1xs|北斗星互联网集成灶（A1消毒柜S款）|1279|
|bdx.i_stove.a1z|北斗星集成灶（A1/C2蒸箱款）|1602|
|bdx.i_stove.c1x|北斗星互联网集成灶（A5/C1/G1消毒柜款）|1216|
|bdx.i_stove.c2x|北斗星互联网集成灶（C2消毒柜款）|1169|
|bdx.i_stove.c5zk|北斗星互联网集成灶(C2/C3蒸烤款)|5136|
|becbas.disposer.e60|贝克巴斯智能厨余垃圾处理器ELEMENT60 PRO|22840|
|becbas.disposer.f3pro|贝克巴斯智能厨余垃圾处理器FUSION3 PRO|24807|
|bj352.waterpuri.k10|352净水器K10|69690|
|bj352.waterpuri.s100cm|352净水器S100|66846|
|bshcn.coffee.181b0w|博世极匠Pro嵌入式咖啡机|83972|
|bshcn.coffee.181w0w|博世极匠Pro嵌入式咖啡机|83973|
|bshcn.coffee.703c09|西门子全自动咖啡机EQ700|83115|
|bshcn.coffee.705c03|西门子EQ700全自动咖啡机|82648|
|bshcn.coffee.707c03|西门子EQ700全自动咖啡机|83585|
|bshcn.coffee.8l1b0w|西门子玄晶Pro嵌入式咖啡机|83975|
|bshcn.coffee.905c03|西门子全自动咖啡机EQ900|83123|
|bshcn.coffee.907c05|西门子EQ900全自动咖啡机|83971|
|bshcn.coffee.9181b0|博世accentLine天工嵌入式咖啡机|83974|
|bshcn.coffee.918l1b|西门子studioLine嵌入式咖啡机|83976|
|bshcn.dishwasher.23eb33|西门子极净魔盒新一级水效智能烘干洗碗机|83900|
|bshcn.dishwasher.25zb24|西门子智净魔方晶蕾洗碗机|83063|
|bshcn.dishwasher.3eb24k|西门子智净魔方洗碗机|84384|
|bshcn.dishwasher.43eb33|智净魔方灶下洗碗机|83664|
|bshcn.dishwasher.43hb25|智净魔方洗碗机|83517|
|bshcn.dishwasher.4ekb88|博世小虎鲸独嵌两用洗碗机|83668|
|bshcn.dishwasher.5zx26m|西门子智净魔方Pro洗碗机|84421|
|bshcn.dishwasher.63hx00|西门子全能舱洗碗机|83047|
|bshcn.dishwasher.65zx00|智净魔方Pro洗碗机|83409|
|bshcn.dishwasher.6mx16c|博世嵌入式洗碗机|83407|
|bshcn.dishwasher.6x26jc|西门子晶蕾洗碗机|83043|
|bshcn.dishwasher.75zx00|西门子全能舱晶蕾洗碗机|83051|
|bshcn.dishwasher.8ix06c|博世6系嵌入式洗碗机|83055|
|bshcn.dishwasher.8s06jc|西门子晶蕾洗碗机|83042|
|bshcn.dishwasher.eb06kc|西门子黑魔镜U7智能烘干洗碗机|83897|
|bshcn.dishwasher.eb11kc|西门子极净魔盒洗碗机|83131|
|bshcn.dishwasher.eb11mc|极净魔盒3.0洗碗机|83510|
|bshcn.dishwasher.eb18mc|西门子极净魔盒新一级水效智能烘干洗碗机|83899|
|bshcn.dishwasher.eb20mc|西门子极净魔盒6.0洗碗机|84670|
|bshcn.dishwasher.eb21mc|西门子极净魔盒6.0洗碗机|84671|
|bshcn.dishwasher.eb24kc|智净魔方Auto洗碗机|83511|
|bshcn.dishwasher.eb26kc|西门子全能舱U7洗碗机|84383|
|bshcn.dishwasher.eb26mc|西门子极净魔盒6.0洗碗机|84672|
|bshcn.dishwasher.eb33kc|西门子全能舱Auto洗碗机|83060|
|bshcn.dishwasher.eb33mc|西门子全能舱Auto洗碗机|83129|
|bshcn.dishwasher.eb63mc|西门子黑魔镜新一级水效智能烘干洗碗机|83898|
|bshcn.dishwasher.eb88kc|极净魔盒3.0洗碗机|83417|
|bshcn.dishwasher.eb88mc|极净魔盒3.0洗碗机|83516|
|bshcn.dishwasher.eb99kc|极净魔盒3.0洗碗机|83415|
|bshcn.dishwasher.ekb11c|博世4系独嵌两用洗碗机|83138|
|bshcn.dishwasher.ekb88c|博世小虎鲸嵌入式洗碗机|83136|
|bshcn.dishwasher.ekw88c|博世小虎鲸嵌入式洗碗机|83133|
|bshcn.dishwasher.ekx00c|博世4系嵌入式洗碗机|83053|
|bshcn.dishwasher.emb99c|博世嵌入式洗碗机|83669|
|bshcn.dishwasher.emw99c|博世小虎鲸嵌入式洗碗机|83666|
|bshcn.dishwasher.es23kc|西门子灶下洗碗机|83130|
|bshcn.dishwasher.ew88kc|极净魔盒3.0洗碗机|83416|
|bshcn.dishwasher.ex00kc|西门子全能舱Auto洗碗机|83036|
|bshcn.dishwasher.ex66kc|西门子隐嵌开门烘干洗碗机|83670|
|bshcn.dishwasher.hb00kc|西门子全能舱洗碗机|83035|
|bshcn.dishwasher.hb03mc|西门子黑魔镜636双核热动力烘干洗碗机|83892|
|bshcn.dishwasher.hb06mc|西门子极净魔盒3.0双核热动力烘干洗碗机|83894|
|bshcn.dishwasher.hb08kc|西门子全能舱洗碗机|83137|
|bshcn.dishwasher.hb11kc|西门子全能舱洗碗机|83052|
|bshcn.dishwasher.hb11mc|西门子极净魔盒Plus洗碗机|83128|
|bshcn.dishwasher.hb24mc|西门子智净魔方洗碗机|83062|
|bshcn.dishwasher.hb25kc|智净魔方灶下洗碗机|83662|
|bshcn.dishwasher.hb25mc|西门子智净魔方洗碗机|83132|
|bshcn.dishwasher.hb55kc|智净魔方灶下洗碗机|83660|
|bshcn.dishwasher.hb66mc|智净魔方洗碗机|83521|
|bshcn.dishwasher.hb88mc|西门子全能舱洗碗机|83050|
|bshcn.dishwasher.hi88mc|西门子全能舱洗碗机|83048|
|bshcn.dishwasher.hkb99c|博世V10灶下新风洗碗机|83514|
|bshcn.dishwasher.hks66c|博世4系嵌入式洗碗机|83056|
|bshcn.dishwasher.hl24mc|西门子下嵌式智能洗碗机|82152|
|bshcn.dishwasher.hl25kc|智净魔方灶下洗碗机|83512|
|bshcn.dishwasher.hl25mc|智净魔方洗碗机|83509|
|bshcn.dishwasher.hl66mc|智净魔方洗碗机|83518|
|bshcn.dishwasher.hmb66c|博世V10嵌入式洗碗机|83135|
|bshcn.dishwasher.hmb99c|博世V10Pro嵌入式洗碗机|83134|
|bshcn.dishwasher.hmx66c|博世V10 Pro新风洗碗机|83513|
|bshcn.dishwasher.hs00kc|西门子全能舱洗碗机|83049|
|bshcn.dishwasher.hs11mc|智净魔方洗碗机|83519|
|bshcn.dishwasher.ht66mc|智净魔方洗碗机|83520|
|bshcn.dishwasher.hx66mc|智净魔方洗碗机|83663|
|bshcn.dishwasher.sn75zx|智净魔方Pro洗碗机|83412|
|bshcn.dishwasher.vb26mc|西门子极净魔盒6.0洗碗机|84673|
|bshcn.dishwasher.vmw06c|博世V20 Pro焕彩版洗碗机|84674|
|bshcn.dishwasher.x00mc|西门子全能舱晶蕾洗碗机|83034|
|bshcn.dishwasher.xb33kc|西门子极净魔盒洗碗机|83046|
|bshcn.dishwasher.y80pcc|西门子智净魔方Pro进口洗碗机|84455|
|bshcn.dishwasher.yc80pc|博世天工系列进口沸石洗碗机|84456|
|bshcn.dishwasher.zb11mc|智净魔方Plus洗碗机|83413|
|bshcn.dishwasher.zb24mc|西门子智净魔方晶蕾洗碗机|83037|
|bshcn.dishwasher.zb25kc|西门子极净魔盒灶下晶蕾洗碗机|83061|
|bshcn.dishwasher.zb26mc|西门子智净魔方Pro洗碗机|84423|
|bshcn.dishwasher.zb28mc|智净魔方Pro洗碗机|83503|
|bshcn.dishwasher.zb29mc|西门子智净魔方Pro洗碗机|84420|
|bshcn.dishwasher.zb58kc|西门子智净魔方灶下新一级水效晶蕾烘干洗碗机|83901|
|bshcn.dishwasher.zb66kc|西门子智净魔方U7 Plus洗碗机|84460|
|bshcn.dishwasher.zb66mc|西门子智净魔方Plus洗碗机|84662|
|bshcn.dishwasher.zb69kc|西门子智净魔方U7 Plus洗碗机|84459|
|bshcn.dishwasher.zb69mc|西门子智净魔方Plus洗碗机|84663|
|bshcn.dishwasher.zb88kc|西门子灶下晶蕾洗碗机|83033|
|bshcn.dishwasher.zb88mc|智净魔方Plus洗碗机|83400|
|bshcn.dishwasher.zb99mc|智净魔方Pro洗碗机|83411|
|bshcn.dishwasher.zc06mc|西门子智净魔方Pro晶蕾烘干洗碗机|83896|
|bshcn.dishwasher.zc25kc|智净魔方灶下洗碗机|83403|
|bshcn.dishwasher.zc66mc|西门子智净魔方Plus洗碗机|84664|
|bshcn.dishwasher.zcz66c|博世进口6系嵌入式洗碗机|83408|
|bshcn.dishwasher.zkc00c|博世Z10灶下沸石洗碗机|83507|
|bshcn.dishwasher.zkx26c|博世Z20灶下沸石洗碗机|84427|
|bshcn.dishwasher.zl24mc|西门子智净魔方Pro洗碗机|84381|
|bshcn.dishwasher.zl26kc|西门子智净魔方U7 Plus洗碗机|84458|
|bshcn.dishwasher.zl26mc|西门子智净魔方Pro洗碗机|84422|
|bshcn.dishwasher.zl66mc|西门子智净魔方Plus洗碗机|84665|
|bshcn.dishwasher.zmb11c|博世Z10 Plus沸石洗碗机|83502|
|bshcn.dishwasher.zmb16c|博世Z20 Plus沸石洗碗机|84669|
|bshcn.dishwasher.zmb26c|博世Z20 Pro沸石洗碗机|84424|
|bshcn.dishwasher.zmb66c|博世Z10洗碗机|84382|
|bshcn.dishwasher.zmb99c|博世Z10 Pro沸石洗碗机|83414|
|bshcn.dishwasher.zmc00c|博世Z10 Pro沸石洗碗机|83504|
|bshcn.dishwasher.zmx00c|博世6系嵌入式洗碗机|83054|
|bshcn.dishwasher.zmx01c|博世Z10 Plus洗碗机|83659|
|bshcn.dishwasher.zmx11c|博世Z10 嵌入式洗碗机|83111|
|bshcn.dishwasher.zmx26c|博世Z20 Pro沸石洗碗机|84425|
|bshcn.dishwasher.zmx66c|博世Z10 Pro 新一级水效沸石烘干洗碗机|83903|
|bshcn.dishwasher.zmx99c|博世Z10 Pro灵动大师沸石洗碗机|83506|
|bshcn.dishwasher.zs11mc|智净魔方Plus洗碗机|83515|
|bshcn.dishwasher.zx06mc|西门子黑魔镜65ZPro晶蕾烘干洗碗机|83895|
|bshcn.dishwasher.zx08mc|智净魔方Pro洗碗机|83402|
|bshcn.dishwasher.zx11mc|智净魔方Plus洗碗机|83508|
|bshcn.dishwasher.zx26mc|西门子智净魔方Pro新一级水效晶蕾烘干洗碗机|83902|
|bshcn.dishwasher.zx28mc|智净魔方Pro洗碗机|83410|
|bshcn.dishwasher.zx55mc|西门子智净魔方Plus洗碗机|84666|
|bshcn.dishwasher.zx66kc|西门子智净魔方U7 Plus洗碗机|84461|
|bshcn.dishwasher.zx66mc|西门子智净魔方Plus洗碗机|84667|
|bshcn.dishwasher.zx68kc|西门子智净魔方U7 Plus洗碗机|84426|
|bshcn.dishwasher.zx68mc|西门子智净魔方Plus洗碗机|84668|
|bshcn.dishwasher.zx88mc|智净魔方Plus洗碗机|83401|
|bshcn.fridge.1ade0c|博世奢嵌10系下嵌式冰箱|84225|
|bshcn.fridge.1hd30c|博世进口嵌入式冰箱|83376|
|bshcn.fridge.2053vc|西门子灵动储鲜多门冰箱|83293|
|bshcn.fridge.21ade0|博世奢嵌10系下嵌式冰箱|84226|
|bshcn.fridge.2aa50c|博世M8s法式多门冰箱|83149|
|bshcn.fridge.2aa99c|博世零嵌活氧净8系多门冰箱|84389|
|bshcn.fridge.2ea20c|博世零嵌6系多门冰箱|84221|
|bshcn.fridge.2ea97c|博世零嵌活氧净6系多门冰箱|84222|
|bshcn.fridge.2va20c|博世零嵌活氧净6系多门冰箱|84217|
|bshcn.fridge.2va97c|博世零嵌活氧净8系多门冰箱|84219|
|bshcn.fridge.6hfd0c|博世奢嵌10系两门冰箱|84387|
|bshcn.fridge.72aa34|西门子恒鲜零度多门冰箱|83381|
|bshcn.fridge.88hva5|西门子零嵌超氧L5多门冰箱|83881|
|bshcn.fridge.8aa26c|博世小平安Z830活氧净十字门冰箱|83868|
|bshcn.fridge.8aa28c|博世零嵌活氧净8系多门冰箱|83880|
|bshcn.fridge.8aa63c|博世维他鲜动力法式多门冰箱|83288|
|bshcn.fridge.8aa99c|博世零嵌活氧净8系多门冰箱|83879|
|bshcn.fridge.8eaa57|西门子零嵌超氧L7多门冰箱|83886|
|bshcn.fridge.8eaa63|西门子零嵌超氧L7多门冰箱|83884|
|bshcn.fridge.8va26c|博世小平安Z620活氧净Lite十字门冰箱|83870|
|bshcn.fridge.8va59c|博世活氧净对开门冰箱|83286|
|bshcn.fridge.92aa25|西门子超氧零度仓3门对开|83377|
|bshcn.fridge.9aa21c|博世全嵌活氧净8系多门冰箱|84520|
|bshcn.fridge.9aa26c|博世全嵌活氧净6系多门冰箱|84517|
|bshcn.fridge.9aa28c|博世全嵌活氧净8系多门冰箱|84519|
|bshcn.fridge.9aa31c|博世全嵌活氧净8系多门冰箱|84518|
|bshcn.fridge.9aw27c|博世全嵌活氧净8系多门冰箱|84524|
|bshcn.fridge.9bv163|西门子平嵌P3十字门冰箱|84105|
|bshcn.fridge.9va26c|博世小平安P625活氧净Plus十字门冰箱|83875|
|bshcn.fridge.aa256c|西门子法式多门零嵌冰箱|82159|
|bshcn.fridge.aa349c|西门子无界Pro超氧真空舱多门冰箱|83122|
|bshcn.fridge.aa657c|西门子无界Pro超氧真空舱多门冰箱|83120|
|bshcn.fridge.bv120c|西门子冰立方平嵌315自动制冰十字门冰箱|84104|
|bshcn.fridge.bv156c|西门子平嵌P3十字门冰箱|84106|
|bshcn.fridge.bv163c|西门子冰立方平嵌315自动制冰十字门冰箱|84103|
|bshcn.fridge.bva56c|西门子冰立方P520超氧Plus十字门冰箱|83873|
|bshcn.fridge.bva58c|西门子冰立方P520超氧Plus十字门冰箱|83871|
|bshcn.fridge.bva61c|西门子冰立方P520超氧Plus十字门冰箱|83874|
|bshcn.fridge.bva63c|西门子冰立方P520超氧Plus十字门冰箱|83872|
|bshcn.fridge.eaa22c|西门子零嵌超氧L7多门冰箱|83885|
|bshcn.fridge.eaa57c|西门子冰立方Z505超氧Lite十字门冰箱|83865|
|bshcn.fridge.eaa63c|西门子冰立方Z710超氧十字门冰箱|83866|
|bshcn.fridge.es20ti|西门子零度多门冰箱|83382|
|bshcn.fridge.fa156c|西门子保鲜大师黑钢法式多门冰箱|83284|
|bshcn.fridge.faa56c|西门子智能eNose零度多门冰箱|83291|
|bshcn.fridge.fva20c|西门子恒鲜零度多门冰箱|83290|
|bshcn.fridge.gaa20c|西门子全嵌超氧Q5十字门冰箱|84512|
|bshcn.fridge.gaa22c|西门子全嵌超氧Q7十字门冰箱|84521|
|bshcn.fridge.gaa50c|西门子全嵌超氧Q7十字门冰箱|84516|
|bshcn.fridge.gaa56c|西门子全嵌超氧Q7十字门冰箱|84514|
|bshcn.fridge.gaa61c|西门子全嵌超氧Q7十字门冰箱|84515|
|bshcn.fridge.gaa63c|西门子全嵌超氧Q5十字门冰箱|84513|
|bshcn.fridge.gaw22c|西门子全嵌超氧Q7十字门冰箱|84522|
|bshcn.fridge.gaw56c|西门子全嵌超氧Q7十字门冰箱|84523|
|bshcn.fridge.hva20c|西门子零嵌超氧L5多门冰箱|83883|
|bshcn.fridge.hva50c|西门子无界Pro超氧零度仓|83586|
|bshcn.fridge.hva56c|西门子冰立方Z505超氧Lite十字门冰箱|83867|
|bshcn.fridge.jpv50c|西门子保鲜大师黑钢冰箱|83587|
|bshcn.fridge.na236c|西门子智感零度中字门|83287|
|bshcn.fridge.naa95c|西门子智感零度冰箱|83379|
|bshcn.fridge.nade0c|西门子奢嵌L9下嵌式冰箱|84227|
|bshcn.fridge.nv141c|西门子恒鲜对开门冰箱|83292|
|bshcn.fridge.nv95t1|西门子控湿保鲜对开门|83378|
|bshcn.fridge.nva22c|西门子恒鲜对开门冰箱|83285|
|bshcn.fridge.nva63c|西门子恒鲜对开门冰箱|83289|
|bshcn.fridge.pa658c|西门子独立式超氧D9对开门冰箱|84388|
|bshcn.fridge.rade0c|西门子奢嵌L9下嵌式冰箱|84228|
|bshcn.fridge.va220c|西门子零嵌L5多门冰箱|84223|
|bshcn.fridge.va256c|西门子零嵌超氧L5多门冰箱|84220|
|bshcn.fridge.va320c|西门子超氧零度舱|83380|
|bshcn.fridge.va356c|西门子零嵌L5多门冰箱|84224|
|bshcn.hood.2bumb9|西门子iQ700双拢双吸3.0顶吸油烟机|84653|
|bshcn.hood.2m90aw|博世8系六维风 Plus顶吸油烟机|84655|
|bshcn.hood.2m98cw|博世8系T10 Pro双吸油烟机|84155|
|bshcn.hood.2m9ubw|博世8系T8 3.0 双吸油烟机|84163|
|bshcn.hood.2p99pw|博世8系T10 Plus双吸油烟机|84156|
|bshcn.hood.2v98aw|博世4系5D Plus 2.0顶吸油烟机|84659|
|bshcn.hood.6v99sw|博世6系六维风 顶吸油烟机|84654|
|bshcn.hood.8m98bw|博世8系T10双吸油烟机|84157|
|bshcn.hood.a0mb9w|西门子iQ500 6D Plus顶吸油烟机|84657|
|bshcn.hood.a5eb9w|西门子iQ100锥锋Air 2.0侧吸油烟机|84148|
|bshcn.hood.a8me9w|西门子iQ700 X9 Pro双吸油烟机|84150|
|bshcn.hood.b52m90|博世6系六维风 Plus顶吸油烟机|84658|
|bshcn.hood.bumb9w|西门子iQ700 X7 Pro 3.0双吸油烟机|84158|
|bshcn.hood.dg5b9w|西门子iQ500 X7 3.0双吸油烟机|84165|
|bshcn.hood.f9vb9w|西门子iQ300 锥锋Air Pro侧吸油烟机|84660|
|bshcn.hood.l9pb9w|西门子iQ700 X9 Pro Max双吸油烟机|83484|
|bshcn.hood.mumb9w|西门子iQ500 X7 3.0双吸油烟机|84164|
|bshcn.hood.numd9w|西门子iQ700 X7 Plus 3.0双吸油烟机|84159|
|bshcn.hood.p9pb9w|西门子iQ700 X9 Pro双吸油烟机|84151|
|bshcn.hood.p9vb9w|西门子iQ300锥锋2.0侧吸油烟机|84661|
|bshcn.hood.r8mb9w|西门子iQ700 X9双吸油烟机|84154|
|bshcn.hood.s8mb9w|西门子iQ700 X9 Plus双吸油烟机|84152|
|bshcn.hood.u8mr9w|西门子iQ700 X9 Plus双吸油烟机|84153|
|bshcn.hood.xumb9w|西门子iQ700 X7 Plus 3.0双吸油烟机|84162|
|bshcn.mfcp.555cbc|博世智能烹饪机Cookit曜黑版|84098|
|bshcn.mfcp.555cwc|博世智能烹饪机Cookit|82167|
|bshcn.oven.0dxb0w|西门子玄晶蒸箱|83432|
|bshcn.oven.0e8b0w|西门子玄晶蒸箱|83427|
|bshcn.oven.0r1b0w|西门子玄晶蒸箱|83429|
|bshcn.oven.11c1b0|西门子蒸玲珑抽屉蒸箱|83581|
|bshcn.oven.14xb1w|博世天工蒸箱|84267|
|bshcn.oven.4dnb1w|西门子iQ300黑魔方蒸烤一体机|83148|
|bshcn.oven.4dnv7w|西门子智魔方W5微蒸烤一体机|84092|
|bshcn.oven.4e9t7w|西门子智魔方W5微蒸烤一体机|84096|
|bshcn.oven.4mlg7w|西门子智魔方W5微蒸烤一体机|84091|
|bshcn.oven.4n5g7w|西门子智魔方W5微蒸烤一体机|84090|
|bshcn.oven.4r7t7w|西门子智魔方W5微蒸烤一体机|84089|
|bshcn.oven.4x9t7w|西门子智魔方W5微蒸烤一体机|84095|
|bshcn.oven.58db1w|博世天工蒸烤一体机|84269|
|bshcn.oven.58gxs6|西门子iQ700蒸烤一体机|83582|
|bshcn.oven.58w5w|博世御器W8微蒸烤一体机|83440|
|bshcn.oven.5b7g2w|西门子智魔方Z3炫彩大屏蒸烤一体机|83436|
|bshcn.oven.5dhg8w|西门子iQ500智魔方炫彩大屏款蒸烤一体机|83147|
|bshcn.oven.5e5w2w|西门子iQ500黑魔方蒸烤一体机|83278|
|bshcn.oven.5mpg2w|西门子iQ500智魔方炫彩大屏款蒸烤一体机|83146|
|bshcn.oven.5n9g6w|西门子智魔方Z5触启蒸烤一体机|83428|
|bshcn.oven.5r7b2w|西门子智魔方蒸烤一体机|82153|
|bshcn.oven.5r8l6w|西门子智魔方Z5触启蒸烤一体机|83433|
|bshcn.oven.5x1v4w|西门子智魔方Z5触启蒸烤一体机|83435|
|bshcn.oven.7364w0|博世极匠Pro蒸烤箱|83583|
|bshcn.oven.78gqb1|西门子studioLine烤箱|83580|
|bshcn.oven.78qb1w|博世天工烤箱|84268|
|bshcn.oven.7e1n3w|西门子智魔方W7微蒸烤一体机|83439|
|bshcn.oven.7mpg5w|西门子iQ700智魔方Pro智瞳款蒸烤一体机|83116|
|bshcn.oven.7nag3w|西门子iQ700智魔方Pro微波款蒸烤一体机|83279|
|bshcn.oven.7r2t3w|西门子智魔方W7微蒸烤一体机|83438|
|bshcn.oven.8e1g4w|西门子智魔方Z5智语蒸烤一体机|83855|
|bshcn.oven.9abs6w|西门子iQ300黑魔方蒸烤一体机|83145|
|bshcn.oven.b93d8w|博世御器Z4炫彩蒸烤一体机|83854|
|bshcn.oven.bdc711|博世蒸如意抽屉蒸箱|83858|
|bshcn.oven.cs589a|西门子iQ300黑魔方蒸烤一体机|83277|
|bshcn.oven.e54d3w|博世御器Z8云瞳蒸烤一体机|83441|
|bshcn.oven.e59m8w|博世御器W6微蒸烤一体机|84097|
|bshcn.oven.e93w6w|博世御器Z6触启蒸烤一体机|83431|
|bshcn.oven.m3hr0w|博世极匠蒸箱|83434|
|bshcn.oven.m3nd8w|博世御器W6微蒸烤一体机|84094|
|bshcn.oven.r13d6w|博世御器Z6智语蒸烤一体机|83856|
|bshcn.oven.r15t8w|博世御器W6微蒸烤一体机|84093|
|bshcn.oven.r59d3w|博世御器W8微蒸烤一体机|83437|
|bshcn.oven.r71d4w|博世御器Z6触启蒸烤一体机|83430|
|bshcn.stove.7nyv6e|西门子studioLine电磁灶|83619|
|bshcn.stove.90dv1e|博世accentLine电磁灶|83616|
|bshcn.waterpuri.050c3c|博世水如意B6 Pro嵌饮机|84264|
|bshcn.waterpuri.060c1c|博世水如意S8 Plus冰热嵌饮机|83364|
|bshcn.waterpuri.060c2c|博世水如意S8 Plus冰热嵌饮机|83365|
|bshcn.waterpuri.0d2c3c|西门子全场景饮水机|84818|
|bshcn.waterpuri.0d2c4c|西门子全场景饮水机|84817|
|bshcn.waterpuri.1b0b1c|西门子iQ500水玲珑温热嵌饮机|84101|
|bshcn.waterpuri.1b3c1c|西门子水玲珑Q5 Pro嵌饮机|84260|
|bshcn.waterpuri.1b4c1c|西门子水玲珑Q5 Pro嵌饮机|84261|
|bshcn.waterpuri.53bb3c|西门子嵌入式智能净饮机|82164|
|bshcn.waterpuri.53bc1c|西门子iQ500水玲珑Pro冰热嵌饮机|83281|
|bshcn.waterpuri.53bc4c|西门子水玲珑500Pro冰热嵌饮机|83367|
|bshcn.waterpuri.54bc1c|西门子iQ500水玲珑温热嵌饮机|83117|
|bshcn.waterpuri.55bc1c|西门子水玲珑500Pro冰热嵌饮机|83366|
|bshcn.waterpuri.60bb1c|西门子三合一嵌饮机|83363|
|bshcn.waterpuri.60bc1c|西门子水玲珑Q7 Pro嵌饮机|84265|
|bshcn.waterpuri.6abb1c|西门子水玲珑Q7嵌饮机|84263|
|bshcn.waterpuri.e1bb1c|博世水如意B6嵌饮机|84403|
|bshcn.waterpuri.e1bc1c|博世水如意B6 Pro嵌饮机|84404|
|bshcn.waterpuri.fsbc1c|博世水如意B8ProS嵌饮机|84819|
|bshcn.waterpuri.fsbc2c|博世水如意B8ProS嵌饮机|84820|
|bshcn.waterpuri.sb0c1c|西门子水玲珑Q7 ProS嵌饮机|84262|
|bshcn.waterpuri.sb0c5c|西门子水玲珑700ProS冰热嵌饮机|83369|
|candor.wine_cool.a|凯腾酒柜（80L/275L）|67460|
|careli.fryer.maf01|米家智能空气炸锅3.5L|3361|
|careli.fryer.maf06a|米家智能空气炸锅 4.5L|12124|
|careli.fryer.ybaf01|悠伴智能空气炸锅2208DTW|6179|
|chunmi.cooker.c301|米家智能小饭煲2|14124|
|chunmi.cooker.cmwy3|米家智能微压IH电饭煲3L|14933|
|chunmi.cooker.cmwy4|米家智能微压IH电饭煲4L|14934|
|chunmi.cooker.eh3|米家智能小饭煲2|8220|
|chunmi.cooker.js5|米家智能快煮电饭煲 5L|8208|
|chunmi.cooker.normal2|米家IH电饭煲|257|
|chunmi.cooker.normal3|米家IH电饭煲 4L|290|
|chunmi.cooker.normal4|米家IH电饭煲 4L|391|
|chunmi.cooker.normal5|米家IH电饭煲|616|
|chunmi.cooker.press2|米家压力IH电饭煲|390|
|chunmi.cooker.zwz02|知吾煮1.6L电饭煲|6234|
|chunmi.health_pot.a1|米家智能多功能养生壶|3012|
|chunmi.i_stove.s1y|米家智能蒸烤一体集成灶S1|10003|
|chunmi.ihcooker.hk1|米家电磁炉|778|
|chunmi.microwave.n20l02|米家微波炉|5753|
|chunmi.microwave.n23l01|米家智能微烤一体机|2442|
|chunmi.oven.tsx8|米家智能微蒸烤一体机|12407|
|chunmi.pre_cooker.dylg5|米家智能电压力锅5L|3498|
|chunmi.pre_cooker.mini1|米家智能电压力锅2.5L|2857|
|coli.waterpuri.nf4645|COLI科淋纳滤智能款净水器|2359|
|cykj.hood.yjc901|cleadeep净味油烟机|2340|
|deerma.mfcp.v1|米家智能多功能蒸煮锅1.5L|4086|
|deerma.mfcp.v2|米家智能多功能蒸煮锅1.5L|6062|
|dicook.cooker.wfz4003|无人炊智能煮饭机器人|66444|
|difeis.ven_fan.dql04h|帝菲斯智能凉霸|70359|
|dilan.ven_fan.v1|DL凉霸|37147|
|era.steriliser.gc01|变频杀菌超声波清洗机|5997|
|era.ysj.b65|博乐宝凉白开净饮机|17206|
|fotile.hood.emd1tmi|云魔方吸油烟机|1037|
|ftd.ven_fan.wfifbh|米科智想凉霸|16265|
|honyar.waterpuri.001|HONYAR鸿雁牌HY-RO401-1000M型反渗透净水机|28458|
|hoto.k_scale.qwcfc|小猴智能厨房秤|4480|
|hoto.k_scale.qwcfc2|小猴智能厨房秤|6222|
|hoto.timer.kt|米家智能计时器|9385|
|hzft.dishwasher.vp10|方太智能洗碗机|81748|
|hzft.hood.358v1|方太智能油烟机|81163|
|hzft.i_stove.da10|方太智能气电两用灶|81236|
|hzft.oven.ep1|方太智能蒸烤一体机|81783|
|hzft.waterpuri.hr7|方太智能净水器|81784|
|imibar.cooker.mbihr3|饭小二煮饭机器人|66454|
|jdj25.waterpuri.001|佳德净天泓反渗透净水器|28931|
|jdjz.waterpuri.dbjx12|京东京造牌JZJS25DBJX-1200G型双出水反渗透净水器|35053|
|jdjz.waterpuri.gcjx12|京东京造牌JZJS25GC-1200G型双出水反渗透净水器|35052|
|jdjz.waterpuri.tjlr01|京东京造牌JZJS26-TJLR01型台式净饮机|35663|
|jguo.waterpuri.jg01|今果牌双出水净水器|28415|
|jguo.waterpuri.jg612|今果牌X901-1200G型厨下式净水器|27887|
|jipin.fryer.my982w|即品智能云可视化空气炸锅|9503|
|jxdh.ven_fan.dh004|智芯凉霸1号Pro|19725|
|jxn.waterpuri.jxnbp2|净小能反渗透净水器|37032|
|jyaiot.cm.ccj01|solista 智能炒菜机|1251|
|jyaiot.cm.jycj01|炒菜机SD-CJ01|5594|
|lge.fridge.fridge|LG无霜冷藏冷冻箱|83099|
|macro.boiler.combgl|万家乐燃气采暖热水炉|83764|
|mibx5.fridge.bd46m|米家冰箱 对开(适用610/636L)|39072|
|midjd.fridge.256b|米家冰箱 ｜ 精巧装 三门256L 冰羽白|15602|
|midjd.fridge.439b|米家冰箱 十字439L/436L 超薄平嵌|17780|
|midjd.fridge.501b|米家冰箱 对开门501L 墨羽岩|15596|
|midjd.fridge.516|米家冰箱 十字对开门520L 墨羽岩|11149|
|midjd.fridge.603|米家冰箱 十字对开门603L 冰晶岩|13306|
|midjd.fridge.bd38l1|米家冰箱 对开门501L 墨羽岩|26804|
|midjd.fridge.bd42l|米家冰箱 对开550L/530L|28775|
|midjd.fridge.bf01l|米家冰箱｜平嵌Q7 法式439L|27689|
|midjd.fridge.bf06e|米家冰箱Pro 双系统 法式平嵌508L|30242|
|midjd.fridge.bf06s|米家冰箱Pro 双系统 法式平嵌508L|22643|
|midjd.fridge.bf06z|米家冰箱Pro 双系统 法式平嵌508L|34579|
|midjd.fridge.bf08n|米家冰箱 法式平嵌400L|36777|
|midjd.fridge.bf08s|米家冰箱 法式平嵌400L|24696|
|midjd.fridge.bf10z|米家冰箱Pro 双系统 法式平嵌508L|34575|
|midjd.fridge.bf11e|米家冰箱Pro 双系统 法式平嵌508L|28205|
|midjd.fridge.bf12l|米家冰箱Pro 双系统 法式513L|28821|
|midjd.fridge.bf12s|米家冰箱Pro 双系统 法式513L|25545|
|midjd.fridge.bf132|米家冰箱Pro 法式508L 全域离子净化4.0|37379|
|midjd.fridge.bf52a|米家冰箱Pro 微冰鲜双系统 法式平嵌560L|35956|
|midjd.fridge.bf53a|米家冰箱Pro 双系统 法式平嵌560L|33594|
|midjd.fridge.bf53s|米家冰箱Pro 双系统 法式平嵌560L 自动制冰|33590|
|midjd.fridge.bs13l|米家冰箱 十字439L/436L 超薄平嵌|27687|
|midjd.fridge.bs13s|米家冰箱 十字439L/436L 超薄平嵌|20911|
|midjd.fridge.bs19s|米家冰箱 十字430L|32298|
|midjd.fridge.bs28s1|米家冰箱 十字门（520L/501L铂银）|20990|
|midjd.fridge.bs32e|米家冰箱Pro 双系统 十字平嵌508L|30243|
|midjd.fridge.bs32s|米家冰箱Pro 双系统 十字平嵌508L|21416|
|midjd.fridge.bs41l|米家冰箱 巨能装 十字513L/十字503L|32165|
|midjd.fridge.bs42l|米家冰箱 巨能装Pro 十字513L|28773|
|midjd.fridge.bs42s|米家冰箱 巨能装Pro 十字513L|22679|
|midjd.fridge.bs42z|米家冰箱 巨能装Pro 十字513L|33019|
|midjd.fridge.bs472|米家冰箱Pro 十字508L 全域离子净化4.0|37380|
|midjd.fridge.bs52a|米家冰箱Pro 微冰鲜双系统 十字平嵌560L|35957|
|midjd.fridge.bs53a|米家冰箱Pro 双系统 十字平嵌560L|33589|
|midjd.fridge.bs53s|米家冰箱Pro 双系统 十字平嵌560L 自动制冰|33588|
|midjd.fridge.bs57s|米家冰箱Pro 双系统 十字606L/米家冰箱Pro 十字 600L|33194|
|midjd.fridge.bx27l|米家冰箱 三门271L|28097|
|midjd6.fridge.430b|米家冰箱 十字对开门430L 墨羽岩|14314|
|midjd6.fridge.430rm|米家冰箱 十字对开门430L 墨羽岩|13415|
|midjd6.fridge.540|米家冰箱 对开门540L 冰晶岩|12495|
|midjd6.fridge.540pro|米家冰箱 对开门尊享版540L|4877|
|midjd6.fridge.5501|米家冰箱 十字四门尊享版550L|4661|
|midjd6.fridge.6101|米家对开门冰箱（适用610L/606L/616L)|10777|
|midjd6.fridge.6103|米家冰箱 对开门610L 冰晶白|13488|
|midjd6.fridge.610b|米家对开门冰箱（适用610L/606L/616L）|14312|
|midjd6.fridge.s16|米家冰箱 十字518L 超薄平嵌|17836|
|midjd7.fridge.4851|米家对开门冰箱 485L|4952|
|midjd9.fridge.x14|米家冰箱 ｜ 精巧装pro 三门303L 制冰版|19336|
|miele.dishwasher.w001|美诺洗碗机|83072|
|minij.fridge.448w|小吉448升智能法式复古冰箱|4708|
|morfun.kettle.mf809|魔凡智能即热茶吧机|68332|
|morfun.ysj.mf208|魔凡智能即热饮水吧|70885|
|morfun.ysj.mf213|魔凡智能即热泡茶机|4698|
|msj.dishwasher.s02|美仕杰集成水槽星云款|12327|
|msj.dishwasher.s110u|美仕杰家用集成水槽|17837|
|msj.f_washer.m1|果蔬净化清洗机|1364|
|msj.f_washer.m1pro|食材净化清洗机|5321|
|msj.f_washer.m2|智能水槽净洗机|3477|
|msj.f_washer.v3|美仕杰集成水槽3.0|7780|
|msj.i_stove.g7|美仕杰集成灶|6847|
|msj.i_stove.jc97|美仕杰集成式燃气灶具|12734|
|msj.i_stove.m3z|美仕杰集成灶魔方款蒸烤|11250|
|msj.i_stove.m6x|美仕杰集成灶魔方款保洁|11249|
|nezha.cooker.x2pro|X2pro-W电饭煲|8831|
|opple.ven_fan.liba01|欧普智能凉霸|12126|
|opple.ven_fan.liba02|欧普智能凉霸|20359|
|our.ven_fan.dq01|奥华凉霸|12620|
|powtek.boiler.24s4|力科壁挂炉启明S4|31324|
|powtek.boiler.s2|mizudo燃气采暖热水炉朔光系列S2|34728|
|qdjm.icemake.fkzbj|JOYMAYLAB方冰制冰机|38368|
|qdjm.icemake.jmzbj|JOYMAYLAB球形制冰机|35573|
|qjiang.ven_fan.a1|QM智能凉霸AI|21955|
|rinnai.boiler.rg68|林内燃气采暖热水炉|82788|
|rixin.health_pot.bmgm01|倍美家智能焖茶壶|16135|
|robam.hood.29a9s|老板电器.油烟机.29A9S|82009|
|robam.hood.81i1|老板电器.油烟机.81-i1|81610|
|roswan.waterpuri.lte01|乐天鹅净水机|22142|
|rrui.k_scale.517|今选智能厨房秤517|38718|
|rrui.k_scale.517b|今选智能厨房秤517B|38719|
|scishare.coffee.s1102|心想智能胶囊咖啡机|201|
|silen.fryer.sck501|Silencare 无言1.8L款空气炸锅|69864|
|silen.fryer.sck505|Silencare 无言智能空气炸锅|69862|
|silen.fryer.sck5o8|Silencare无言智能空气炸锅SC-K508W|5762|
|silen.mfcp.sck307|Silencare无言智能牛排机SC-K307W|71205|
|smith.w_soften.cxs05ta1|佳尼特智能软水机|67029|
|smith.waterpuri.cxr1k|佳尼特智能净水器CXR1000-A1/T1|4273|
|smith.waterpuri.cxr600|佳尼特智能净水器CXR600-A1/T1|4191|
|smith.waterpuri.cxr800|佳尼特智能净水器CXR800-A1/T1|4272|
|smith.waterpuri.jnt600|佳尼特智能净水器|66367|
|tata.milkheat.bl1108|bololo暖奶器|4937|
|uvfive.steriliser.maine|FIVE智能刀筷杀菌架|6638|
|uvfive.steriliser.tiger|FIVE智能刀筷砧板杀菌架|4075|
|vatti.hood.i11x9t|华帝油烟机|82469|
|vihtb.boiler.a1xq|菲斯曼智能壁挂炉|84173|
|vihtb.boiler.v100|菲斯曼燃气壁挂炉|82840|
|vihtb.boiler.v101|菲斯曼冷凝燃气壁挂炉|84465|
|viomi.cooker.v1|云米互联网IH电饭煲|66084|
|viomi.cooker.v2|云米互联网电饭煲（4L 尊享版）|66382|
|viomi.cooker.v4|云米互联网IH电饭煲3L（降糖版）|68044|
|viomi.cooker.v5|云米互联网低糖电饭煲3L|70678|
|viomi.dishwasher.v01|云米互联网洗碗机（8套嵌入式）|672|
|viomi.dishwasher.v03|云米互联网洗碗机（嵌入式）|66386|
|viomi.dishwasher.v05|云米互联网水槽洗碗机|67211|
|viomi.dishwasher.v06|云米互联网洗碗机（嵌入式）|68737|
|viomi.dishwasher.v08|云米互联网洗碗机嵌入式0803A|69771|
|viomi.dishwasher.v09|云米互联网洗碗机4套台面式0402|70264|
|viomi.dishwasher.v10|云米互联网洗碗机10套嵌入式0805|70751|
|viomi.dishwasher.v11|云米互联网洗碗机10套嵌入式0804|71003|
|viomi.dishwasher.v12|云米互联网洗碗机嵌入式0803B|71689|
|viomi.dishwasher.v14|云米互联网洗碗机10套嵌入式0807|4687|
|viomi.dishwasher.v15|云米AI洗碗机Milano 15套|7090|
|viomi.dishwasher.v17|云米AI洗碗机Super|8066|
|viomi.fridge.b1|云米互联网冰箱（对开门380L）|68138|
|viomi.fridge.b3|云米互动大屏冰箱（十字四门408L）|68897|
|viomi.fridge.b4|云米互动大屏冰箱（对开门458L）|69755|
|viomi.fridge.b5|云米冰箱21Face（十字四门451L）|70497|
|viomi.fridge.b6|云米互动大屏冰箱(对开门518L)|72074|
|viomi.fridge.b7|云米互动大屏冰箱(对开门450L)|72075|
|viomi.fridge.b9|云米互动大屏冰箱(对开门446L)云小鲜系列|72507|
|viomi.fridge.p1|云米互联网冰箱iLive（对开门 598L）|66607|
|viomi.fridge.u1|智能冰箱iLive|442|
|viomi.fridge.u12|云米互联网冰箱 十字四门398/415L 定频|66555|
|viomi.fridge.u13|云米互联网冰箱 十字四门415L/416L|66552|
|viomi.fridge.u15|云米互联网冰箱iLive（法式 365L）|66775|
|viomi.fridge.u17|云米互联网冰箱 十字四门398/415L|67261|
|viomi.fridge.u18|云米互联网冰箱iLive（对开门 485L）|67512|
|viomi.fridge.u2|云米互联网冰箱iLive 对开门版|729|
|viomi.fridge.u24|云米互联网冰箱（对开门450L）|68989|
|viomi.fridge.u25|云米互联网冰箱（法式345L）|68990|
|viomi.fridge.u26|云米冰箱iLive（对开门552L）|69186|
|viomi.fridge.u28|云米冰箱iLive（十字四门450L）|69385|
|viomi.fridge.u29|云米冰箱iLive（法式355L）|69387|
|viomi.fridge.u30|云米冰箱iLive（对开门566L）|69388|
|viomi.fridge.u31|云米冰箱iLive（十字四门508L）|69626|
|viomi.fridge.u32|云米冰箱iLive（对开门456L）|70031|
|viomi.fridge.u34|云米冰箱iLive（对开门640L）|70059|
|viomi.fridge.u35|云米冰箱iLive（十字四门410L）|70060|
|viomi.fridge.u36|云米互联网冰箱iLive（十字四门506L）|70061|
|viomi.fridge.u37|云米互联网冰箱iLive（对开门 528L）|70373|
|viomi.fridge.u38|云米互联网冰箱iLive（对开门 568L）|70424|
|viomi.fridge.u39|云米冰箱iLive2（十字四门485L）|70832|
|viomi.fridge.u4|云米互联网冰箱对开门ilive 483L|65759|
|viomi.fridge.u40|云米冰箱iLive（法式四门416L）|70833|
|viomi.fridge.u41|云米互联网冰箱iLive2(对开门639L)|71503|
|viomi.fridge.u42|云米互联网冰箱iLive2(十字门509L)|71504|
|viomi.fridge.u43|云米互联网冰箱iLive2(法式四门445L)|71505|
|viomi.fridge.u44|云米互联网冰箱iLive2(十字四门513L)|71506|
|viomi.fridge.u45|云米互联网冰箱iLive2(法式四门508L)|71507|
|viomi.fridge.u46|云米互联网冰箱iLive(对开门456L)升级版|4319|
|viomi.fridge.u47|云米互联网冰箱iLive2(对开门590L)|4432|
|viomi.fridge.u49|云米AI智能冰箱iLive2(十字四门450L)语音版|6317|
|viomi.fridge.u50|云米AI智能冰箱iLive2(十字四门518L)语音版|6319|
|viomi.fridge.u51|云米AI智能冰箱iLive2(对开门636L)|6465|
|viomi.fridge.u55|云米AI冰箱Cross E(对开646)|12051|
|viomi.fridge.u56|云米AI冰箱Smart E（十字412）|12432|
|viomi.fridge.u57|云米互联网冰箱iLive（对开456）|12579|
|viomi.fridge.u58|云米AI冰箱Smart E(对开456)|13132|
|viomi.fridge.u6|云米互联网冰箱ilive十字四门486L|65973|
|viomi.fridge.u60|云米AI冰箱Master 3Y（十字536）|13394|
|viomi.fridge.u62|云米AI冰箱Super 2S（对开550）|13878|
|viomi.fridge.u64|云米AI冰箱Smart E(对开456)|15074|
|viomi.fridge.u68|云米AI冰箱Master 3(法式400)|17522|
|viomi.fridge.u69|云米AI冰箱Super 2Pro(十字502)|17794|
|viomi.fridge.u7|云米互联网冰箱ilive 对开门545L|65974|
|viomi.fridge.u70|云米AI冰箱Super 2S(法式509)|17798|
|viomi.fridge.u71|云米AI冰箱Super 2S(十字508)|17869|
|viomi.fridge.u73|云米AI冰箱Master 3E（十字520）|20062|
|viomi.fridge.u8|云米互联网冰箱iLive（对开门 603L）|66058|
|viomi.fridge.v3|云米智能冰箱法式 iLive语音版|645|
|viomi.fridge.w1|云米互联网冰箱 iLive2（三门 301L）|587|
|viomi.fridge.w2|云米互联网冰箱 iLive2（双门 272L）|705|
|viomi.fridge.x11|云米互联网冰箱21Face (对开门 525L)|67400|
|viomi.fridge.x12|云米互联网冰箱21Face（T型三门 408L）|67498|
|viomi.fridge.x13|云米冰箱21Face（法式520L）|68714|
|viomi.fridge.x14|云米冰箱21Face（十字四门516L）|68715|
|viomi.fridge.x15|云米冰箱21Face (对开门522L)|69184|
|viomi.fridge.x17|云米冰箱21Face（对开门450L）|69417|
|viomi.fridge.x19|云米冰箱21Face（对开门635L）|70062|
|viomi.fridge.x20|云米冰箱21Face（十字四门502L）|70063|
|viomi.fridge.x21|云米冰箱21Face (对开门630L)|70756|
|viomi.fridge.x22|云米冰箱 21Face (法式510L)|70350|
|viomi.fridge.x23|云米冰箱21Face（十字四门510L）|70459|
|viomi.fridge.x24|云米冰箱21Face（法式四门 516L）|70685|
|viomi.fridge.x25|云米冰箱21Face（对开门456L）|70686|
|viomi.fridge.x26|云米冰箱YMDK01|71000|
|viomi.fridge.x28|云米冰箱21Face(十字四门502L)|71073|
|viomi.fridge.x29|云米冰箱21Face（法式四门505L）|71074|
|viomi.fridge.x35|云米互联网冰箱21Face(对开门610L)|72282|
|viomi.fridge.x37|云米AI冰箱21Face2(对开门525L)智目版|72775|
|viomi.fridge.x38|云米AI冰箱21Face2(十字四门506L)智目版|72776|
|viomi.fridge.x4|云米互联网冰箱21Face(对开门450L)|787|
|viomi.fridge.x44|云米AI智能冰箱21Face2(对开门525L)智目版|73596|
|viomi.fridge.x48|云米AI冰箱21Face 2S(对开640)|75100|
|viomi.fridge.x49|云米AI冰箱21Face 2S(十字502)|75101|
|viomi.fridge.x50|云米AI冰箱21Face 2PRO(T型门515）|75169|
|viomi.fridge.x7|云米互联网冰箱21Face（428L）|66684|
|viomi.fryer.v2|云米互联网空气炸锅 5L|14586|
|viomi.health_pot.c2|云米互联网养生壶 Honey Pro|68961|
|viomi.hood.a10|云米互联网油烟机 Free 3|66767|
|viomi.hood.a11|云米互联网侧吸油烟机|68784|
|viomi.hood.a12|云米互联网油烟机（自动开合版）|68783|
|viomi.hood.a9|云米互联网油烟机（欧式）|66169|
|viomi.hood.c1|云米油烟机Cross|606|
|viomi.hood.c13|云米AI油烟机 Flash2(VK711)|71786|
|viomi.hood.c14|云米AI油烟机Cross2 X1(VK712)|71787|
|viomi.hood.c15|云米互联网油烟机 Cross3 A1|71788|
|viomi.hood.c16|云米互联网油烟机 Wing 1C|71789|
|viomi.hood.c17|云米互联网油烟机 Free 3 Pro|71790|
|viomi.hood.c19|云米AI油烟机Wing A1|5590|
|viomi.hood.c2|云米互联网油烟机 Cross2|66768|
|viomi.hood.c21|云米AI油烟机 Cross2 A1|5918|
|viomi.hood.c24|云米AI油烟机Super 2 Max|8914|
|viomi.hood.c25|云米AI油烟机 Smart|8999|
|viomi.hood.c26|云米AI油烟机 Super|10438|
|viomi.hood.c28|云米AI油烟机 Cross3 A1|10703|
|viomi.hood.c29|云米AI油烟机 Super Pro|10704|
|viomi.hood.c3|云米互联网油烟机（智能升降版）|68782|
|viomi.hood.c30|云米AI油烟机 Flash|11769|
|viomi.hood.c33|云米AI油烟机Master 3 Pro|12792|
|viomi.hood.c35|云米AI油烟机 Super 2 Pro|13899|
|viomi.hood.c36|云米AI油烟机 Super 2|17227|
|viomi.hood.c37|云米AI油烟机 Super 2 Pro|17447|
|viomi.hood.c39|云米AI油烟机 Smart 2|17851|
|viomi.hood.c4|云米互联网油烟机Flash Pro|68839|
|viomi.hood.c41|云米AI油烟机Super 3（曜石黑）|18259|
|viomi.hood.c42|云米AI油烟机 Smart 2 Pro|18723|
|viomi.hood.c43|云米AI油烟机Super 3（皓月白）|19116|
|viomi.hood.c44|云米AI油烟机 Cross 3E|19843|
|viomi.hood.c47|云米AI油烟机 智享|22099|
|viomi.hood.c5|云米互联网油烟机 Cross 3|68937|
|viomi.hood.c7|云米互联网油烟机|70768|
|viomi.hood.c8|云米互联网油烟机VK707|70965|
|viomi.hood.h1|云米互联网油烟机Hurri标准版|605|
|viomi.hood.h3|云米互联网油烟机 Hurri2|66766|
|viomi.hood.h4|云米互联网油烟机Wing（AI手势操控版）|67630|
|viomi.hood.h5|云米互联网油烟机 Flash|68687|
|viomi.i_stove.v1|云米互联网集成灶|66448|
|viomi.i_stove.v14|云米AI集成灶 Smart|10951|
|viomi.i_stove.v3|云米互联网集成灶（天然气/液化气）|67412|
|viomi.i_stove.v4|云米互联网集成灶（蒸烤一体版）|68818|
|viomi.i_stove.v5|云米互联网集成灶（蒸箱版）|69087|
|viomi.i_stove.v6|云米互联网集成灶 A1(消毒柜版)|71781|
|viomi.i_stove.v7|云米AI集成灶 Milano（蒸烤一体）|71782|
|viomi.i_stove.v8|云米AI集成灶 Navi2（蒸烤一体）|71783|
|viomi.juicer.v2|云米破壁料理机（静音版）|65794|
|viomi.oven.so1|云米互联网蒸烤一体机King（嵌入式）|66721|
|viomi.oven.so2|云米互联网蒸烤一体机 Queen（嵌入式）|66971|
|viomi.oven.so3|云米互联网蒸烤一体机 King Pro (嵌入式)|68153|
|viomi.oven.so5|云米AI蒸烤一体机Face|71339|
|viomi.oven.so6|云米互联网蒸烤一体机Face（嵌入式）|71758|
|viomi.oven.so8|云米AI蒸烤一体机Face A1（嵌入式）|4843|
|viomi.steriliser.v1|云米互联网消毒柜（嵌入式 尊享版）|67371|
|wanhe.boiler.nb4ls|万和壁挂炉零冷水款|82609|
|wanhe.boiler.nbs|万和壁挂炉智能款|82779|
|wanhe.dishwasher.x60|万和洗碗机|83955|
|wanhe.hood.clean|万和抽油烟机净烟款|84277|
|wanhe.hood.l36s6|万和抽油烟机经典款|83647|
|wn001.boiler.bgl|威暖壁挂炉X5|34080|
|wxjzkj.kettle.lxj001|李享佳智能电茶炉|8217|
|wxjzkj.kettle.lxj002|T1智能语音电茶炉|14601|
|xckj.dishwasher.idw01|圈厨嵌入式互联网洗碗机|68204|
|xckj.fridge.111wg2|圈厨111L家用智能冰柜|69537|
|xckj.fridge.151wg1|圈厨家用智能冰柜|68068|
|xckj.fridge.448ws4|圈厨梵希法式四门冰箱|67775|
|xckj.hood.s9001|圈厨S90智联油烟机|68995|
|xckj.hood.z9001|圈厨Z90智开油烟机|67722|
|xckj.waterpuri.ihwp01|圈厨即热净化一体机|68205|
|xckj.waterpuri.js01|圈厨家用净水器|68110|
|xiaomi.cooker.cmihp3|米家智能IH电饭煲P1 3L|22470|
|xiaomi.cooker.cmp1|米家智能变压IH电饭煲 4L|25071|
|xiaomi.fryer.maf16|米家智能空气炸锅P1 6.5L|18475|
|xiaomi.health_pot.p1|米家智能多功能养生壶 P1|18011|
|xiaomi.health_pot.p1v3|米家智能多功能养生壶P1|31728|
|xiaomi.juicer.p1v2|米家智能轻音变频破壁机P1|32524|
|xiaomi.juicer.s2v2|米家智能轻音破壁机S2|32523|
|xiaomi.kettle.mek01|米家智能电热水瓶 5L|13079|
|xiaomi.oven.p1|米家智能微蒸烤一体机P1 28L|19764|
|xptech.kettle.xp001|享泡智能电热水壶|22968|
|xxll.fridge.mtb40g|星星智能冰柜|17905|
|ydzl.waterpuri.t1|优点cuber智能即热净饮机|1071|
|yimilx.icemake.ymzbj|宜米小型制冰机i3|36656|
|yimilx.ysj.ip300p|宜米净饮机IP300pro|24069|
|yimilx.ysj.ip600|宜米净饮机iP600W|24072|
|yimilx.ysj.ip600p|宜米台式反渗透净饮机iP600pro|30871|
|yimilx.ysj.yc1w|宜米制冰速热饮水机YC-1W|19770|
|yimilx.ysj.yc1w2|宜米制冰饮水机YC-1W|24624|
|yimilx.ysj.yc2w|YiMi宜米牌制冰速热饮水机YC-2W|26314|
|yimilx.ysj.yc3|YiMi 宜米牌YC-3型饮水机|34982|
|ym001.ysj.ymbx|炎米智能便携饮水机Y1|36785|
|ym001.ysj.ymd36|炎米智能上水器|38606|
|ym001.ysj.ymysj|炎米智能饮水机|29147|
|ym001.ysj.ymysj3|炎米智能便携饮水机|33360|
|ym001.ysj.ymzm|炎米智能即热饮水机Y1|36786|
|yoda.k_scale.cy80|拜杰智能烘焙营养秤BJ26|14981|
|yoda.k_scale.e2|凯丰智慧烘焙秤E2|16938|
|yoda.k_scale.x3|凯丰智慧烘焙秤X3|16939|
|yunmi.hood.c48|云米AI吸油烟机Super（升级）|25148|
|yunmi.hood.c49|云米鲲鹏Pro AI油烟机|25149|
|yunmi.hood.c51|云米鲲鹏Max油烟机|30042|
|yunmi.hood.c52|云米鲲鹏2油烟机|32789|
|yunmi.kettle.r1|云米智能即热饮水吧（MINI）|556|
|yunmi.kettle.r2|云米智能即热饮水吧（MINI）|65593|
|yunmi.kettle.r3|云米智能即热饮水吧1A（4L版）|65730|
|yunmi.kettle.r7|云米1秒即热饮水机Tee Pro 4L|69754|
|yunmi.kettle.v9|米家恒温电水壶Pro|1497|
|yunmi.plmachine.mg2|云米1秒即热管线机|662|
|yunmi.w_soften.vs100|云米AI中央软水机1.6T|31382|
|yunmi.waterpuri.c5|云米互联网净水器C1（500G）|66771|
|yunmi.waterpuri.f1|云米互联网净水器Fast3（400G 白）|68886|
|yunmi.waterpuri.f2|云米互联网净水器Fast3（600G 白）|68887|
|yunmi.waterpuri.f3|云米互联网净水器Fast3（800G 白）|68888|
|yunmi.waterpuri.f4|云米互联网净水器Easy3（400G)|68889|
|yunmi.waterpuri.f5|云米互联网净水器Easy3（600G)|68890|
|yunmi.waterpuri.f6|云米互联网净水器Easy3（800G)|68891|
|yunmi.waterpuri.f7|云米泉先互联网净水器 Fast3 1000G|4214|
|yunmi.waterpuri.f8|云米泉先互联网净水器 澎湃1000G|4215|
|yunmi.waterpuri.lx2|小米净水器|187|
|yunmi.waterpuri.lx4|小米净水器|486|
|yunmi.waterpuri.lx6|小米净水器厨下式|707|
|yunmi.waterpuri.mg5|云米1秒即热管线机|68160|
|yunmi.waterpuri.s10|云米泉先互联网净水器 super 1200G|71099|
|yunmi.waterpuri.s11|云米互联网净水器 小蓝调（400G）|70023|
|yunmi.waterpuri.s12|云米互联网净水器 小蓝调（600G）|70024|
|yunmi.waterpuri.s14|云米·泉先互联网净水器 小白龙 600G|71703|
|yunmi.waterpuri.s15|云米泉先互联网净水器小海豚 400G|4216|
|yunmi.waterpuri.s16|云米泉先互联网净水器 小海豚 600G|4217|
|yunmi.waterpuri.s17|云米泉先互联网净水器Fast3 800G|4218|
|yunmi.waterpuri.s18|云米泉先互联网净水器 Mee 600G|4219|
|yunmi.waterpuri.s19|云米泉先AI净水器Super Pro 1000G|4220|
|yunmi.waterpuri.s20|云米泉先AI净水器Super Pro 1200G|4221|
|yunmi.waterpuri.s21|云米泉先AI 1秒即热净水器 Super Pro|6383|
|yunmi.waterpuri.s23|云米泉先AI净水器Super Pro 1200G|7115|
|yunmi.waterpuri.s25|云米泉先AI净水器小京龙|7886|
|yunmi.waterpuri.s26|云米泉先AI 净水器小蓝调|7887|
|yunmi.waterpuri.s27|云米泉先AI净水器Cross 3 1000G+|7888|
|yunmi.waterpuri.s28|云米泉先AI净水器 蓝调+|7889|
|yunmi.waterpuri.s29|云米泉先AI净水器 Super S|8361|
|yunmi.waterpuri.s3|云米互联网净水器S2（400G）|66216|
|yunmi.waterpuri.s30|云米泉先AI净水器 Super Y|8362|
|yunmi.waterpuri.s31|云米泉先AI 1秒即热净水器 Super Pro|10671|
|yunmi.waterpuri.s32|云米泉先AI净水器 Super 2 Max|11118|
|yunmi.waterpuri.s33|云米泉先AI净水器 space|11119|
|yunmi.waterpuri.s34|云米泉先AI净水器 Super S|11121|
|yunmi.waterpuri.s35|云米泉先AI净水器 Super Y|11122|
|yunmi.waterpuri.s36|云米泉先AI净水器 Super Y(富锶版)|13352|
|yunmi.waterpuri.s37|云米AI净水器 蓝调 2|13558|
|yunmi.waterpuri.s38|小海豚 2 AI净水器|13915|
|yunmi.waterpuri.s39|云米泉先AI净水器 Super 2|16327|
|yunmi.waterpuri.s4|云米互联网净水器S2（500G）|66393|
|yunmi.waterpuri.s41|云米AI净水器 Super 2S (富锶矿泉)|17518|
|yunmi.waterpuri.s42|云米昆仑4 3升开水矿泉净水器|17898|
|yunmi.waterpuri.s43|云米AI净水器 Super 2+|17899|
|yunmi.waterpuri.s49|云米泉先AI净水器小海豚+|19445|
|yunmi.waterpuri.s5|云米互联网净水器S2（600G）|66773|
|yunmi.waterpuri.s50|云米AI净水器 Super 2Y|19446|
|yunmi.waterpuri.s55|云米AI净水器Super 2Y Plus|19456|
|yunmi.waterpuri.s56|云米AI昆仑矿泉净水机Super 2E|19457|
|yunmi.waterpuri.s57|云米AI净水器 小白龙+|20190|
|yunmi.waterpuri.s58|云米AI净水器 Smart|20191|
|yunmi.waterpuri.s60|云米AI净水器黑豹|21277|
|yunmi.waterpuri.s61|meekee AI净水器小锦鲤|21799|
|yunmi.waterpuri.s62|云米AI昆仑矿泉即热净水机Super 2Pro|21947|
|yunmi.waterpuri.s63|云米AI昆仑矿泉即热净水机Master 5Pro|21948|
|yunmi.waterpuri.s65|云米AI净水器Cross 5|22114|
|yunmi.waterpuri.s66|云米AI净水器Master 3|23752|
|yunmi.waterpuri.s67|云米AI净水器小海豚2|23873|
|yunmi.waterpuri.s68|云米昆仑4矿泉净水器弱碱|24669|
|yunmi.waterpuri.s71|云米AI净水器小京龙Pro|25263|
|yunmi.waterpuri.s73|云米昆仑4矿泉净水器弱碱Pro|27109|
|yunmi.waterpuri.s74|云米AI净水器小京龙900|27289|
|yunmi.waterpuri.s75|云米昆仑4矿泉净水器弱碱Ultra|27789|
|yunmi.waterpuri.s77|云米昆仑4矿泉净水器弱碱Pro（白富镁）|28338|
|yunmi.waterpuri.s78|云米AI鲲鹏净热净水器|28444|
|yunmi.waterpuri.s79|云米昆仑3矿泉净水器 2S Pro|29230|
|yunmi.waterpuri.s80|云米AI净水器小京龙Pro Max|29480|
|yunmi.waterpuri.s81|云米大师系列大通量净水器1400G|29715|
|yunmi.waterpuri.s82|云米大师系列大通量净水器1600G|29716|
|yunmi.waterpuri.s83|云米昆仑4矿泉净水器弱碱Ultra（3升开水）|30333|
|yunmi.waterpuri.s84|云米净水器小京龙2 Pro|30630|
|yunmi.waterpuri.s85|云米全屋净水机领袖套系OW|31871|
|yunmi.waterpuri.s86|云米厨下净水器小京龙3|32998|
|yunmi.waterpuri.s9|云米泉先互联网净水器 super|69805|
|yunmi.waterpuri.s90|云米矿泉净水器昆仑4 Pro Max|34374|
|yunmi.waterpuri.s91|云米矿泉净水器昆仑4 Pro Max（白富镁）|34375|
|yunmi.waterpuri.s92|云米厨下净水器大师900|34419|
|yunmi.waterpuri.s93|云米厨下净水器冠军600G|34420|
|yunmi.waterpuri.s94|云米厨下净水器小京龙3 Max|34421|
|yunmi.waterpuri.s95|云米厨下净水器冠军1000G|34422|
|yunmi.waterpuri.s96|云米矿泉净水器昆仑3(白富镁)|34862|
|yunmi.waterpuri.s97|云米净热净水器鲲鹏2 Max|35952|
|yunmi.waterpuri.s99|云米矿泉净水器昆仑4净热版|37523|
|yunmi.waterpuri.x10|云米泉先AI 1秒即热净饮机X2|68924|
|yunmi.waterpuri.x11|云米泉先AI 1秒即热净饮机X2 mini|5254|
|yunmi.waterpuri.x12|云米泉先AI 1秒即热净饮机 X2 Face|73278|
|yunmi.waterpuri.x13|云米泉先AI 1秒即热净饮机 X2 mini Mango|5873|
|yunmi.waterpuri.x2|云米1秒即热净水器X3优享版|66067|
|yunmi.waterpuri.x7|云米1秒即热净水器X1|66892|
|yunmi.waterpuri.x8|云米1秒即热免安装净饮机X2|68797|
|yunmi.waterpuri.x9|云米1秒即热免安装净饮机 X2 Face|68923|
|yunmi.waterpurifier.v3|小米净水器厨下式|174|
|yunmi.waterpurifier.vtl_v2|小米净水器（虚拟）|140|
|yunmi.ysj.mg12|云米AI冷热管线机Super 2 Pro|27650|
|yunmi.ysj.mg6|云米泉先1秒即热管线机|74235|
|yunmi.ysj.mg7|云米泉先AI管线机 Master 3|13294|
|yunmi.ysj.mg8|云米泉先AI冷热管线机 Super 2E|13382|
|yunmi.ysj.mg9|云米泉先AI管线机 Master 2S|17099|
|yunmi.ysj.x1|云米泉先AI 1秒即热净饮机X2 mini Mango 智联版|8103|
|yunmi.ysj.x12|云米昆仑4Pro台式净饮机冰水版|33628|
|yunmi.ysj.x2|云米泉先AI净饮机 X2|11324|
|yunmi.ysj.x3|云米泉先AI净饮机 Super 2|13947|
|yunmi.ysj.x5|云米昆仑4冰块冷热水矿泉净饮机|17900|
|zjyg.dishwasher.zzy01|智能烘洗式洗碗机|67994|

### 安防

|model|name|pd_id|
|---|---|---:|
|913101.tracker.d1|qborn小海豚儿童安全座椅手机版|9108|
|bc1869.lock.t002|E206Mi|2053|
|bdf668.lock.mf24n|贝德弗智能锁|27928|
|beck.lock.v10|BECK智能门锁V10 Max|29338|
|bull.lock.z10|公牛门锁Z10-M|35590|
|bull.lock.z33m|公牛门锁Z33-M|36201|
|buyang.lock.u9|BUYANG智能门锁U9|40194|
|chuangmi.camera.021a04|小米智能摄像机  云台版Pro|69018|
|chuangmi.camera.036a02|小白智能摄像机 云台版Y2|69511|
|chuangmi.camera.039c01|小米智能摄像机2 云台版|77496|
|chuangmi.camera.046b02|小白智能摄像机 云台版Y2|73289|
|chuangmi.camera.046c04|小米智能摄像机 云台版SE+|75655|
|chuangmi.camera.049a01|小米智能摄像机2 云台版|73488|
|chuangmi.camera.055a02|小白智能全景球机 Q1|73620|
|chuangmi.camera.070a02|小白智能摄像机|79172|
|chuangmi.camera.ip029a|小米智能摄像机 云台版2K|68216|
|chuangmi.camera.ipc013|小白智能摄像机青春版|65731|
|chuangmi.camera.ipc017|小白智能摄像机大众版1080P|66204|
|chuangmi.camera.ipc019|小米智能摄像机 云台版|66703|
|chuangmi.camera.ipc020|小白智能摄像机 户外云台版 N系列|66710|
|cnbi.lock.pf7260|盼盼智能锁PF7260|33563|
|cnbi.lock.pf7270|盼盼智能锁PF7270|33552|
|cnbi.lock.pl7230|盼盼智能锁 PL7230|32835|
|dayi.safe.dy|大一智能保险箱|32235|
|dsm.lock.h3|小嘀智能指纹锁H3|1420|
|dsm.lock.q3|Q3|1203|
|dsm.lock.q3p|德施曼智能锁Q3P|12669|
|dsm.lock.r5|小嘀人脸识别智能锁R5|1370|
|dtwl.camera.dtz3m|德泰智能摄像机2K云台版|22201|
|dun.cateye.nknk500|DUN智能猫眼|65771|
|duoqin.safe.pbfv01|指静脉识别私密箱|1459|
|easc.alarm.biv1|建筑倾斜振动安全监测仪|3737|
|fengyu.intercom.beebird|极蜂智能网络对讲机|67734|
|fimi.camera.c1b|米家小相机|699|
|haman.lock.b10m|MANIS JAVANICA（穿山甲）智能门锁 B10|32361|
|haman.lock.mxb6h|MANIS JAVANICA（穿山甲）智能门锁 门小宝6号|32360|
|honyar.lock.ld2138|鸿雁iHouse智能门锁D2 Pro|28629|
|honyar.lock.ll1101|鸿雁iHouse智能门锁L1|28628|
|hooson.lock.tf22|卿刻云智锁一握开T1|18292|
|htcx.alarm.dt210|航天常兴智慧用电探测器DT-210|9299|
|huohe.lock.m1|果加智能门锁M1|1572|
|hutlon.lock.v0001|汇泰龙超薄屏下指纹智能锁U1|2016|
|iccssi.lock.02|艾栖MX智能门锁|13921|
|iccssi.lock.dlx01|德力西电气智能门锁HDMC-M32J|23480|
|iccssi.lock.ds01|戴司智能门锁M30PRO|26112|
|iccssi.lock.k8plus|艾栖智能门锁Z6-PLUS+|26708|
|iccssi.lock.m30max|戴司智能门锁M30Max|26670|
|iccssi.lock.m32hs|德力西电气智能门锁M32HS|26671|
|iccssi.lock.y3|奥克斯智能锁Y3|20521|
|imou99.camera.tp2|乐橙智能摄像机云台版|67941|
|insistek.tracker.wa620|米哇定位豆|269|
|isa.camera.df3|大方智能摄像机(1080P云台版)|490|
|isa.camera.hl5|小圆智能摄像机|65573|
|isa.camera.hlv3c|华来小方室外摄像机 2K版|73131|
|isa.camera.isc5|小方智能摄像机|282|
|isa.camera.isc5c1|小方智能摄像机|434|
|isa.camera.panjd1|小方智能摄像机 云台版|74965|
|isa.camera.qf3|华来小方智能摄像机（双摄版）|654|
|isa.camera.virtual|小方智能摄像机组|336|
|isa.cateye.hldb6|华来小方智能门铃2 Pro|68722|
|isa.lock.hlsl01|华来小方智能挂锁|5379|
|jdjz.lock.m10pro|京东京造M10 pro智能门锁|28695|
|jgwj.lock.jogh1|JOG 智能U型锁 H1|35715|
|jhm888.lock.dm35|德盾智能锁DM-35|33106|
|jiwu.lock.jwp01|贝尔森智能门锁JW-P|4032|
|jooan.camera.548910|喵眼摄像机|17512|
|kaadas.lock.m91|凯迪仕全自动智能锁 K9-S（M）|10099|
|kkd.lock.a6|金凯德3D人脸识别智能门锁A6|28791|
|kkd.lock.c11|金凯德智能门锁C11|31066|
|kkd.lock.ss1|Dracle智能门锁S1|29082|
|kl2019.lock.f07|帕拉玫智能锁F7|35509|
|kl2019.lock.f7|帕拉玫智能锁X7|24769|
|kl2019.lock.h01|帕拉玫智能锁M7|24770|
|kl2019.lock.s320|帕拉玫半自动智能锁S320|25036|
|kl2019.lock.x10g|帕拉玫智能锁X10-G|38118|
|lcrmcr.lock.cb2207|CRMCR卡唛智能玻璃门锁|11450|
|lcrmcr.lock.cb2306|CRMCR卡唛智能玻璃门锁Pro|15514|
|lcrmcr.safe.20mini|卡唛米克mini智能屏下指纹保管箱|4951|
|lcrmcr.safe.25z|卡唛安诺指纹保管箱25Z|8765|
|lcrmcr.safe.30j|CRMCR卡唛复古机械智能保管箱|10652|
|lcrmcr.safe.30mk|卡唛米刻指纹保管箱|5734|
|lcrmcr.safe.46mn|CRMCR卡唛米诺智能单抽保管柜|19674|
|lcrmcr.safe.46yn|CRMCR卡唛雅诺智能保管箱|15953|
|lcrmcr.safe.46yne|卡唛雅诺电子指纹保管箱|36462|
|lcrmcr.safe.55kn2|CRMCR卡唛卡诺抽柜智能保管柜|23007|
|lcrmcr.safe.an35sidz|卡唛安诺电子保管箱|1120|
|lcrmcr.safe.an35sizw|卡唛安诺指纹保险箱|1057|
|lcrmcr.safe.d60ht|卡唛百宝智能保险柜|5453|
|lcrmcr.safe.kmzb53|卡唛智能保管箱|13702|
|lcrmcr.safe.mp|CRMCR安诺电子指纹保管箱PRO|15890|
|lcrmcr.safe.ms|卡唛米尚电子指纹保管箱|21902|
|lcrmcr.safe.ms30b|卡唛指纹保管箱|1393|
|lcrmcr.safe.ms30mp|卡唛安诺电子指纹保管箱PRO|3298|
|lcrmcr.safe.ms55kn|卡唛卡诺智能保管箱|2617|
|lcrmcr.safe.ms80b|卡唛臻宝人脸识别保险柜|2255|
|lcrmcr.safe.msh|卡唛米尚人脸识别智能保管箱|29610|
|lcrmcr.safe.msx|卡唛米宝智能保险柜|39966|
|lcrmcr.safe.sd003|卡唛水滴型智能保管箱|6715|
|lcrmcr.safe.x142|卡唛mini智能复古保管箱|6079|
|line.lock.bmsc1|LineHope智能玻璃门锁C1|10305|
|line.lock.bmsc1s|LineHope智能玻璃门锁C1S|13559|
|line.lock.fms2|方舟鱼智能门锁S2|13981|
|line.lock.fms21|方舟鱼智能门锁S2E|37547|
|line.lock.fms5|智能门锁S5|17213|
|line.lock.fms5s|智能门锁S5 Pro|22171|
|line.lock.fms6|方舟鱼智能门锁S6|17274|
|line.lock.fms7|方舟鱼智能门锁S7|17276|
|line.lock.fms8|方舟鱼AI屏智能门锁A7|17278|
|line.lock.fzjms|方舟鱼全自动掌静脉智能锁A1|21112|
|line.lock.ms2|LineHope智能门锁S2|12381|
|line.lock.mst1|TATACASA智能门锁NJJ-102|20501|
|line.lock.mst2|TATACASA智能门锁NJJ-101|20502|
|line.lock.zjmsa2|方舟鱼全自动人脸智能锁A2|21759|
|linp.doorbell.g03|自发电WiFi门铃|1196|
|linp.doorbell.g04|自发电WIFI门铃2|4265|
|lkd001.doorbell.amlkml|LKD智能门铃M10|31787|
|loock.camera.c1k|鹿客智能看护AI摄像机|76155|
|loock.cateye.v01|鹿客智能猫眼青春版CatY|65618|
|loock.cateye.v07|鹿客智能猫眼CatX|74942|
|loock.lock.401|鹿客AI智能锁 V6 Max|26239|
|loock.lock.401m|鹿客AI智能门锁 V6 Max 双屏版|38757|
|loock.lock.401n|鹿客智能门锁 V5 全景版|39424|
|loock.lock.416|鹿客一握开智能锁|24223|
|loock.lock.416yd|云丁一握开智能锁|28112|
|loock.lock.417|鹿客一握开视频锁|24641|
|loock.lock.418|鹿客掌脉锁 S7|25306|
|loock.lock.419a|鹿客指脉锁 P9|25309|
|loock.lock.419yd|云丁全自动智能门锁|28844|
|loock.lock.cc2s|鹿客智能门锁Classic 2|2415|
|loock.lock.cc2xpro|鹿客智能门锁Classic 2X Pro|3343|
|loock.lock.fcl112|鹿客智能锁S50M Pro|8561|
|loock.lock.fcl201|鹿客智能锁V5 Max|9877|
|loock.lock.fvl109|鹿客猫眼智能锁S50M|7735|
|loock.lock.fvl202|鹿客智能锁V5 Pro|9878|
|loock.lock.ojjz1|OJJ智能门锁Z1|1763|
|loock.lock.p50|鹿客指静脉智能锁P50|8229|
|loock.lock.pfvl10|鹿客猫眼智能锁R1M|5450|
|loock.lock.s30|鹿客全自动推拉门锁S30 Pro|3063|
|loock.lock.s30v2|鹿客全自动推拉门锁S30|3629|
|loock.lock.s50f|鹿客人脸智能锁S50F|7559|
|loock.lock.v1|鹿客智能门锁Classic|571|
|loock.lock.v14|鹿客智能门锁 蜘蛛侠系列限量版|1690|
|loock.lock.v15|鹿客智能门锁X1/X3|4365|
|loock.lock.v16|鹿客指静脉全自动门锁SV40|4546|
|loock.lock.v3|鹿客智能门锁Q2|896|
|loock.lock.v4|OJJ智能门锁X1|1020|
|loock.lock.v7|鹿客智能门锁Classic 2X|1285|
|loock.lock.v8|鹿客智能门锁Classic 2S|1284|
|loock.lock.v9|鹿客智能门锁Smart|1319|
|loock.lock.xfvl10|鹿客指静脉智能锁S50|7012|
|loock.lock.zb692|ZIGBANG 全自动人脸掌脉可视门锁 R81|36969|
|lumi.lock.bmcn02|小米智能门锁|1433|
|lumi.lock.v1|智能锁芯|411|
|lumi.sensor_dlock.v1|门锁传感器|249|
|madv.alarm.winlock1|叮零窗户限位报警器 智能版|68303|
|madv.cateye.dlc5jz|叮零智能视频门铃C5|71388|
|madv.cateye.dle3jz|叮零智能视频门铃E3|71389|
|madv.cateye.dle4jz|叮零视频门铃E6|75253|
|madv.cateye.dlowl|叮零智能视频门铃|65594|
|madv.cateye.dlowle|叮零智能视频门铃E3|69812|
|madv.cateye.dlowlplus|叮零智能视频门铃S|66712|
|madv.cateye.dlowlse|叮零智能视频门铃C3|69020|
|madv.cateye.dlowlse2|叮零智能视频门铃C5|69021|
|madv.cateye.mi3iot|小米智能门铃3|75158|
|madv.cateye.miowlv2|小米智能门铃2|67121|
|madv.cateye.miv2jz|小米智能门铃2|71387|
|madv.doorbell.dltxq|叮零智能控制提醒器|15908|
|meihua.lock.k70pro|梅花智能锁A6|17997|
|mexin.lock.dz268|美心智能锁DZ268|37909|
|mexin.lock.k20s|美心智能锁MX-K20S|34730|
|miir.camera.ir01|单反遥控|65715|
|minuo.tracker.lm001|冉物智能防丢器|1298|
|miot.camera.spec|标准插件摄像机Hook设备(不要删除)|75679|
|miot.doorbell.spec|标准插件HOOK设备（删除会影响线上所有插件运行，千万勿删，非常重要）|77281|
|miot.lock.cctest|智能蓝牙门锁|15529|
|miot.lock.qqaly|Qqara 蓝牙智能门锁|7646|
|miot.lock.test06|mijia智能门锁|15522|
|miot.lock.v000|mijia门锁2|15527|
|miot.lock.x2|佳能蓝牙智能门锁|7874|
|mwonly.lock.s60m|王力智能锁|23273|
|mxiang.camera.mwc10|小米室外摄像机电池版（室内机）|69615|
|mxiang.cateye.mdb10|小默智能可视门铃|66994|
|mxiang.cateye.xmcatt1|小默智能猫眼|66285|
|ola.lock.i3|Ola智能木门锁Mars|1036|
|px123.lock.h6|掌航智能门锁H6|22546|
|px123.lock.m2|palmhang掌航智能指纹门锁M2|25037|
|qcy.camera.c1pro|QCY智能摄像机CC1S|70169|
|savlm.lock.v23|SAVLM智能锁|21692|
|seeyes.lock.138mbh|星月智能锁XYC138M-BH|33072|
|sfy.lock.d001|索菲亚智能人脸掌静脉门锁M1|31971|
|shjszn.lock.c1|榉树智能锁|407|
|shjszn.lock.kx|榉树智能门锁KX|1039|
|simto.lock.xk1zrm|新多智能门锁XK-1ZRM|36549|
|simto.lock.xq3zrm|新多智能门锁XQ-3ZRM|36850|
|sjdoor.lock.sfa1|神将智能门锁SFA1|33138|
|sjdoor.lock.sqa2|神将智能门锁SQA2|33520|
|sjdoor.lock.sqq2|神将智能门锁SQQ2|37619|
|sjj.lock.m1|石将军智能门锁 M1|12352|
|sxs.lock.001|锁先森智能门锁|17170|
|sxs.lock.d1pro|锁先森智能门锁D1pro|24864|
|sxs.lock.d30|锁先森智能门锁D30|31024|
|sxs.lock.s1|锁先森人脸识别智能门锁S1|26139|
|t3ft.safe.001|三斧头密码抽屉T3|18771|
|tatamm.lock.m2|尼克智能锁M2|29155|
|tecche.lock.a20|特畅恒智能门锁A20|25054|
|viomi.lock.lbt12a|云米蓝调系列智能门锁(3D人脸版)|22712|
|viomi.lock.lbt13a|云米蓝调系列智能门锁(大屏猫眼版)|22361|
|viomi.lock.lbt14a|云米互联网智能门锁eLink 2A|5005|
|viomi.lock.lbt16a|云米AI智能门锁Super 2Y|17345|
|viomi.lock.lbt16b|云米蓝调系列智能门锁(人脸猫眼版)|22362|
|viomi.lock.lbt41e|云米AI智能门锁eyeLink 2F Pro|7000|
|viomi.lock.lbt46a|云米AI智能门锁Master 3E|15595|
|viomi.lock.lbt48a|云米AI智能门锁eyeLink 2S|7984|
|viomi.lock.lbt51a|云米AI智能门锁Smart 2|7985|
|viomi.lock.lbt61a|云米AI智能门锁Super 2E（蓝牙版）|12460|
|viomi.lock.lbt64a|云米AI智能门锁Super 3Y|18301|
|viomi.lock.link1|云米互联智能门锁Link（蓝牙版）|1300|
|viomi.lock.link2|云米互联智能门锁Link（长续航版）|2412|
|viomi.lock.link2p|云米互联网智能门锁eLink 2Pro|5647|
|viomi.lock.link2v|云米互联网智能门锁eyeLink 2V|5646|
|viomi.lock.link3|云米AI智能门锁eLink 2C|3597|
|viomi.lock.link4s|云米互联网智能门锁eyeLink 2F|5414|
|voc777.lock.757|小K士人脸门锁|10763|
|voc777.lock.k5ss|VOC全自动掌静脉门锁|19328|
|voc777.lock.k6|VOC全自动门锁|18165|
|voc777.lock.t20pro|VOC智能门锁T50 Max|28410|
|voc777.lock.t30pro|VOC猫眼视频人脸锁|15680|
|voc777.lock.t8|VOC大屏猫眼人脸锁T10 Plus|11958|
|wzxj.lock.l7|卿刻智能门锁L7|24820|
|wzxj.lock.mo|卿刻智能门锁Mo|24817|
|wzxj.lock.mopro|卿刻智能门锁Mo Pro|24818|
|wzxj.lock.t2pro|卿刻智能门锁T2Pro|25531|
|wzxj.lock.t5|卿刻T5智能门锁|16744|
|wzxj.lock.t5e|卿刻智能门锁T5E|24825|
|wzxj.lock.t5pro|卿刻智能门锁T5pro|24815|
|xiaomi.camera.c01a02|小米智能摄像机 云台版2K|7692|
|xiaomi.lock.m40|小米智能门锁 5 Max|24854|
|xiaovv.camera.bp340|xiaovv户外枪球一体摄像机|78399|
|xiaovv.camera.bq36|xiaovv海螺枪球摄像机 BQ3|81086|
|xiaovv.camera.c1|xiaovv智能婴儿监视器|70173|
|xiaovv.camera.c12k|xiaovv智能婴儿监护器 2K|72917|
|xiaovv.camera.fj12|叮零智能双摄海螺机 H2|81415|
|xiaovv.camera.fj13|叮零智能云台摄像机 X3 Pro|81620|
|xiaovv.camera.fj19|叮零智能云台摄像机 X8|29695|
|xiaovv.camera.fj20|叮零室外双摄摄像机 A8|30808|
|xiaovv.camera.fj22|叮零婴儿看护摄像机|36996|
|xiaovv.camera.fjcam2|智能双摄摄像机S1云台版|79768|
|xiaovv.camera.fjcam3|叮零室外双摄摄像机A1|80159|
|xiaovv.camera.fjcam4|叮零智能双摄摄像机 S8|80197|
|xiaovv.camera.fjcam5|叮零户外云台摄像机 4G|80493|
|xiaovv.camera.fjcam6|叮零智能摄像机 N1|80494|
|xiaovv.camera.fjcam8|叮零智能云台摄像机 X3|81038|
|xiaovv.camera.fjcam9|叮零室外云台摄像机 B1|81213|
|xiaovv.camera.lamp|壁灯摄像机|67441|
|xiaovv.camera.ljcam1|烈驹智能云台半球机 2K|80081|
|xiaovv.camera.p1|xiaovv户外云台摄像机 2K|71562|
|xiaovv.camera.p124g|xiaovv户外云台摄像机 4G|78798|
|xiaovv.camera.p12l|户外云台摄像机 青春版|76486|
|xiaovv.camera.p94mp|xiaovv户外云台摄像机 Pro 2.5K|75575|
|xiaovv.camera.ptz|户外云台摄像机|67440|
|xiaovv.camera.q1|xiaovv智能云台海螺机|71565|
|xiaovv.camera.q12|xiaovv智能云台摄像机 心享版|71582|
|xiaovv.camera.q2|xiaovv智能云台摄像机 智享版|73404|
|xiaovv.camera.q24mp|xiaovv智能云台摄像机 智享版2.5K|75565|
|xiaovv.camera.q2lite|小猫云台摄像机 青春版|76120|
|xiaovv.camera.q330|xiaovv智能云台海螺机2.5K|78227|
|xiaovv.camera.q4|欧森智能摄像机 2K|79439|
|xiaovv.camera.q8|xiaovv智能云台摄像机 2K|71563|
|xiaovv.camera.q9|xiaovv智能云台摄像机 2K 双光版|79440|
|xiaovv.camera.svp940|safeV户外云台摄像机 Pro 2.5K|76752|
|xiaovv.camera.xv4g2|xiaovv户外云台摄像机 4G 2.5K|80080|
|xiaovv.camera.xva3|xiaovv智能全景摄像机|65536|
|xiaovv.camera.xvb4|xiaovv 户外摄像机|66319|
|xiaovv.camera.xvcb2|户外摄像机 Pro|68734|
|xiaovv.camera.xvcb3|xiaovv户外摄像机 Pro 2K|69465|
|xiaovv.camera.xvd5|xiaovv智能全景摄像机（云存储版）|66316|
|xiaovv.camera.xvsnowman|智能云台摄像机|68569|
|xiaovv.camera.xvvc02|xiaovv室内枪球一体摄像机 BQ2 Pro|82002|
|xiaovv.camera.xvvc04|xiaovv 户外云台摄像机 2.5K SE|82306|
|xiaovv.camera.xvvc08|xiaovv智能婴儿监护器 4K|29265|
|xiaovv.camera.xvvc11|xiaovv智能云台摄像机 Q2 4K|36998|
|ydhome.cateye.pr1|优点智能门铃R1|67264|
|ydhome.lock.c1p|优点智能锁C1P|1415|
|ydhome.lock.lkd10|优点智能锁乐可多系列-10|33054|
|ydhome.lock.lkd15|优点智能锁乐可多系列-15|33426|
|ydhome.lock.lkd3|优点智能锁乐可多系列LKD3|31883|
|ydhome.lock.m2lite|优点智能锁M2Lite|2995|
|ydhome.lock.m2p|优点智能锁M2 Pro|2818|
|ydhome.lock.m2silver|优点智能锁M2|955|
|ydlock.lock.l88|云丁智能锁L88-ULtra|37054|
|ydlock.lock.l89|云丁智能锁L89-ULtra|37055|
|ydlock.lock.l90|云丁智能锁L90-ULtra|33468|
|ydlock.lock.q67max|云丁智能锁Q67-Max|37906|
|ydlock.lock.q69max|云丁智能锁Q69-Max|38500|
|yh8888.lock.dz6622|樱花智能锁DZ-6622|28882|
|yh8888.lock.dz6636|樱花智能锁DZ-6636|33801|
|yh8888.lock.dzf32|樱花智能锁DZ-F32|28883|
|yh8888.lock.sh18m|樱花智能锁DZ-H18M|33896|
|yh8888.lock.sx10m|惠氏智能锁S-X10M|34172|
|yingji.safe.stb01|SITERB斯特堡卡度保险箱|23634|
|yingji.safe.stbjy|SITERB斯特堡金悦保险箱|24916|
|yingji.safe.stbms|SITERB斯特堡洛可保险箱|24918|
|yingji.safe.stbyw|SITERB斯特堡悦威保险箱|24917|
|ynsur.lock.m1|因硕智能锁M1|26404|
|ynsur.lock.m1pro|因硕智能门锁M1 Pro|31507|
|ynsur.lock.q16v1|因硕智能锁Q16|23797|
|ynsur.lock.s11m|因硕智能锁S11m|26403|
|ynsur.lock.s12m|因硕智能锁S12m|26402|
|ynsur.lock.t13|ynsurT13智能锁|23635|
|ynsur.lock.t30m|因硕智能门锁T30m|28486|
|ynsur.lock.v12m|因硕智能门锁V12m|27068|
|yunlu.door.sd2101|云鹿智能门P1|9768|
|yunlu.door.sd2103|云鹿智能门U|9770|
|yunlu.door.sd2104|云鹿智能门Y|9771|
|yunlu.door.sd2105|云鹿智能门Young|10000|
|yunlu.door.sd2106|云鹿智能门P50|10001|
|yunlu.door.sd2107|云鹿智能门K2|14412|
|yunlu.door.sd2108|云鹿智能门Young|14413|
|yunlu.door.sd2110|云鹿智能门Classic|15508|
|yunlu.door.sd2111|云鹿智能门P50|32870|
|yunlu.door.sd2112|智能门Classic|15640|
|yunmi.camera.cwb12b|云米AI智能摄像机Smart（云台版2.5K）|25388|
|yunmi.lock.lbt11c|云米蓝调系列智能门锁（基础版）|25943|
|yunmi.lock.lbt14a|云米蓝调系列智能门锁（掌静脉人脸猫眼版）|25944|
|yunmi.lock.lbt81a|云米AI智能门锁Cross 3|25947|
|yunmi.lock.lbt81b|云米蓝调AI智能门锁E|28242|
|yunmi.lock.lwb89a|云米鲲鹏AI智能门锁 Pro|25945|
|yunshi.lock.s2|夏洛克智能贴锁M1|373|
|yunyi.camera.v1|小蚁智能摄像机|13|
|zhaomu.safe.bgx45l|博凡W系列保管箱|3725|
|zjhdgm.lock.m1|CHJH智能门锁M2|29415|
|zjhdgm.lock.m2|CHJH智能门锁M1|29647|
|zsdl.lock.v38|大德利嵌入式人脸智能锁V38|33828|
|zsdl.lock.v6|大德利V6人脸视频智能锁|30832|

### 宠物与植物

|model|name|pd_id|
|---|---|---:|
|209754.fishbowl.tank01|森森智能鱼缸ATE|36025|
|afour.s_lamp.001|紫物智能消毒杀菌灯|69175|
|binuo.feeder.y1|比诺智能喂食器Y1|35996|
|booer.feeder.001|猫特勒宠物智能喂食器|16776|
|haibao.pet_waterer.mm2|伺宠官智能宠物饮水机|7962|
|hddz.s_lamp.uvl38w|小达杀菌消毒灯WiFi版|2912|
|hfjh.fishbowl.600|画法几何智能模块化生态鱼缸|7106|
|hfjh.fishbowl.c500|画法几何两栖生态底滤鱼缸|71040|
|hfjh.fishbowl.h100x|画法几何智能鱼缸 M1|21756|
|hfjh.fishbowl.m1max|画法几何智能鱼缸M1 Ultra|27735|
|hfjh.fishbowl.v1|画法几何智能鱼缸|67805|
|hfjh.fishbowl.v2|画法几何C系智能鱼缸|69621|
|hhcc.plantmonitor.v1|花花草草监测仪|152|
|hsg.fishbowl.hxs01|海享说智能生态缸|11691|
|huoman.feeder.pf20i|霍曼Real智能喂食器|82494|
|huoman.litter_box.co1|霍曼头等舱净味盒|2023|
|huoman.litter_box.cs106|霍曼智能猫砂盆|82304|
|jxdh.pet_waterer.cw001|大豪智芯宠物饮水机1号Pro|19724|
|madv.feeder.fjpet1|叮零智能宠物喂食器|23827|
|madv.feeder.fjpet2|叮零智能宠物喂食器|27088|
|miot.pettoy.bbb|test-lljyj|74953|
|mmgg.feeder.bowl|Pawbby智能宠物碗|2922|
|mmgg.feeder.petfeeder|米家智能宠物喂食器|66532|
|mmgg.feeder.snack|Pawbby智能宠物零食机|67427|
|mpmiot.pettoy.v1|毛绒派智能宠物陪伴球|6889|
|petjc.litter_box.pro|聚宠 畅行 智能猫砂盆 Pro|23006|
|petkit.feeder.p570|小佩.宠物喂食器.p570|81712|
|pio.flowerpot.ivy01|PlantsIO智能萌宠花盆Ivy|74954|
|qwliot.fishbowl.38000|黑擎智能水质监测器|9217|
|sansi.s_lamp.uv0a01|三思智能杀菌灯|29862|
|sansi.s_lamp.uv0a02|三思智能杀菌灯plus|30986|
|skyrc.feeder.dfeed|湃妮双餐喂食器|5435|
|skyrc.feeder.fed|湃妮迷你宠物喂食器|68402|
|skyrc.feeder.mini2|湃妮迷你宠物喂食器2|6469|
|skyrc.feeder.mmfed|湃妮定时多餐喂食器|4635|
|skyrc.feeder.vdfeed|湃妮迷你可视宠物喂食器|71401|
|skyrc.feeder.vfed|湃妮智能可视喂食器|68157|
|skyrc.pet_waterer.fre1|湃妮智能宠物饮水机|67685|
|skyrc.pet_waterer.fres2|湃妮迷你宠物饮水机Pro|5903|
|uvfive.s_lamp.slmap2|FIVE智能消毒杀菌灯|68812|
|vson.fishbowl.86861|叮零智能鱼缸|24218|
|wfxx.fishbowl.ysb2|默恋 喂食器|16208|
|xiaovv.feeder.fj14|叮零宠物视频喂食器|81772|
|xqdzsw.feeder.001|猫特勒智能宠物喂食器Pro|30209|
|ymt.flowerpot.sp|一米田智能水培种植机|13190|
|ymt.flowerpot.test01|一米田智能水培种植机YMT-SP-202601|34791|
|ymt.flowerpot.v1|一米田智能种植伴侣|2692|
|ymt.flowerpot.v3|一米田智能花盆|5531|
|yunzyo.feeder.t001|猫特勒宠物喂食器|17676|
|ywzs.flowerpot.ywzs01|酷小鲸智能种植器|19100|
|ziwooo.s_lamp.uvc|紫物智能消毒杀菌灯Pro|70276|

### 影音娱乐

|model|name|pd_id|
|---|---|---:|
|090615.wifispeaker.x6bj|X6背景音乐(PTX)|75434|
|adp.robot.ad|艾达普 手指机器人|12861|
|aimei.avamp.box1|咪哒音视频功放F1|23783|
|asu.projector.apro|Redmi投影仪 Pro|76457|
|asu.projector.cronus|小米全色激光影院|71081|
|asu.projector.proja|Redmi投影仪|74967|
|bwos.wifispeaker.yx01|元响智能音响（520）|24340|
|cebs.avamp.amp01|科恩贝斯CEBS智能影院音视频功放|24708|
|cgllc.clock.cgc1|青萍蓝牙小钟|3132|
|cgllc.clock.dove|青萍蓝牙闹钟|1398|
|chuangmi.radio.v2|小米网络收音机增强版|287|
|dangb.projector.dbd7x|当贝智能激光投影仪-D7X|82775|
|dangb.projector.dbd7xh|当贝智能激光投影仪-D7X Pro 超亮版|84179|
|dangb.projector.dbd7xm|当贝智能激光投影仪-D7X 超亮版|84464|
|dangb.projector.dbd7xp|当贝智能激光投影仪-D7X Pro|82774|
|dangb.projector.dbs2|当贝智能投影仪-Smart2|82776|
|dangb.projector.dbs7u|当贝智能激光投影仪-S7 Ultra Max|82548|
|dangb.projector.dbx7m|当贝智能激光投影仪-X7 Max|82772|
|dangb.projector.dbx7p|当贝智能激光投影仪-X7 Pro|82773|
|dangb.projector.dbx7u|当贝智能激光投影仪-X7 Ultra|82741|
|dangb.projector.dbx9m|当贝智能激光投影仪-X9 Max|84733|
|dangb.projector.dbx9p|当贝智能激光投影仪-X9 Pro|84731|
|dangb.projector.dbx9u|当贝智能激光投影仪-X9 Ultra|84734|
|fengmi.projector.015fc2|小明 Q2 智能投影仪|73724|
|fengmi.projector.015fc3|小明 Q3 智能投影仪|77546|
|fengmi.projector.015fco|小明 0101M 投影仪|79288|
|fengmi.projector.015fo2|小明 Q5 智能投影仪|79966|
|fengmi.projector.015fo3|小明C015FCB-X2智能投影仪|81215|
|fengmi.projector.015fo5|小明C015FCB-X3智能投影仪|81787|
|fengmi.projector.015fo6|小明C015FCB-Pro智能投影仪|82016|
|fengmi.projector.025fc2|小明 Q2 Pro 智能投影仪|76467|
|fengmi.projector.025fc3|小明 Q3 Pro 智能投影仪|76494|
|fengmi.projector.025fc5|小明XMM3101智能投影仪|80972|
|fengmi.projector.045fc|峰米 S5 激光投影仪|75397|
|fengmi.projector.055fc|峰米 R1 Nano 超短焦激光投影仪|73737|
|fengmi.projector.146fc|峰米 V10 4K 投影仪|73738|
|fengmi.projector.166fc2|峰米激光电视 Cinema 3|73730|
|fengmi.projector.196fc|峰米 X5 4K 激光投影仪|76495|
|fengmi.projector.206ac3|光峰 B300T 激光家庭影院|73726|
|fengmi.projector.206fc3|峰米 T2 激光电视|73728|
|fengmi.projector.c015|小明 Q1 迷你投影仪|72416|
|fengmi.projector.c025|小明 Q1 Pro 智能投影仪|71236|
|fengmi.projector.c045fc|小明 Q3 Max 智能投影仪|76493|
|fengmi.projector.c065f|小明 0601 投影仪|78873|
|fengmi.projector.c066f|小明 0611 投影仪|79287|
|fengmi.projector.fm05|米家投影仪 青春版|65838|
|fengmi.projector.fm15|米家激光投影仪|782|
|fengmi.projector.fm154k|米家激光投影电视4K|65812|
|fengmi.projector.l065f|峰米 X1 激光投影仪|72414|
|fengmi.projector.l115fx|峰米 R1 超短焦激光投影仪|71779|
|fengmi.projector.l166|A300臻彩激光电视|66650|
|fengmi.projector.l166f|峰米激光电视 Cinema 2|72410|
|fengmi.projector.l176|峰米激光电视4K Cinema|66651|
|fengmi.projector.l176fp|峰米激光电视4K Cinema Pro|68682|
|fengmi.projector.l185|米家激光投影仪|67260|
|fengmi.projector.l185j2|小米激光投影仪 1S|73624|
|fengmi.projector.l206a|光峰激光家庭影院 A300|71235|
|fengmi.projector.l206fx|峰米激光电视 T1|72413|
|fengmi.projector.l206j|小米激光影院2 4K|71234|
|fengmi.projector.l246|C700 4K智能直投激光家庭影院|66666|
|fengmi.projector.l306a|光峰D30激光家庭影院|68680|
|fengmi.projector.l406f|峰米激光影院4K MAX|70320|
|fengmi.projector.l406q|峰米 × 腾讯极光 4K 激光影院 Max|71619|
|fengmi.projector.m055|峰米投影仪 Smart|66335|
|fengmi.projector.m055d|峰米投影仪Smart Lite|67163|
|fengmi.projector.m085j|米家投影仪2|68679|
|fengmi.projector.m135f|峰米投影仪Vogue|66866|
|fengmi.projector.m135fp|峰米投影仪Vogue Pro|1846|
|fengmi.projector.m135jp|米家投影仪2 Pro|68747|
|hgzjjs.avamp.51m|华歌MINI5.1智能影K音视频功放|18345|
|hgzjjs.avamp.72m|华歌智能影K功放CIC-MINI-7.2-MIC|18346|
|hgzjjs.avamp.mini51|华歌MINI5.1智能影院音视频功放|18344|
|hlwch.clock.ddla1m|当当狸UFO夜灯小闹钟A1（M）|28828|
|hope.avamp.s12|向往智能5.1影K功放|83215|
|hope.wifispeaker.4plus|单音源音乐|76141|
|hope.wifispeaker.5plus|向往智能5.1影音主机|81813|
|hope.wifispeaker.box3x|背景音乐|72554|
|hope.wifispeaker.m9|向往M9|72557|
|hope.wifispeaker.mini3a|向往Mini 3A|70948|
|hope.wifispeaker.mini3s|单音源背景音乐|72956|
|hope.wifispeaker.pad3s|双音源背景音乐|70851|
|hope.wifispeaker.s11|向往智能5.1影K主机|82200|
|hyin.avamp.amp1|昊音智能影K影院功放|33247|
|inovel.projector.me2|分体式智能投影|764|
|jiqid.mistory.ipen1|机器岛智能点读笔|964|
|jiqid.mistory.pro|米兔智能故事机|66199|
|jiqid.mistory.zjj|儿童智能机器人|68164|
|jiqid.robot.cube|智能魔方|1249|
|jmgo.projector.k310cn|坚果智能投影仪-N1S系列|83246|
|jmgo.projector.k620cn|坚果智能投影仪-Migo系列|84435|
|jmgo.projector.k631cn|坚果投影仪N1 Air超亮版 / X3 Air超亮版|82600|
|jmgo.projector.k633cn|坚果投影仪N1 Air 旗舰版|83156|
|jmgo.projector.k931cn|坚果智能投影仪-N5系列|82943|
|jmgo.projector.k961|坚果智能投影仪-X3 Plus|82859|
|jmgo.projector.k976cx|坚果智能投影仪-X系列|83852|
|jmgo.projector.kd11|坚果智能投影仪-N系列|83758|
|jmgo.projector.ocean|坚果智能投影仪-P5X/P5S|82250|
|jmgo.projector.t910co|坚果激光电视O3系列|82864|
|jmgo.projector.viola|坚果智能投影仪-N3 Plus|82084|
|jmgo.projector.violin|坚果智能投影仪-N3|82190|
|kpin.clock.l9|康品智能时钟L9|32650|
|liany.avamp.amp1|泊声智能影K功放|35962|
|liany.wifispeaker.yx01|泊声涂趣智能音响|80281|
|longwa.clock.air1|Air时钟X1|15319|
|miaomiaoce.clock.ht02|秒秒测温湿智能时钟|1747|
|miir.dvd.ir01|DVD遥控|65720|
|miir.projector.ir01|投影仪遥控|65719|
|miir.stb.ir01|机顶盒遥控|65722|
|miir.tv.hir01|酒店红外电视|70717|
|miir.tv.ir01|电视遥控|65725|
|miir.tvbox.ir01|电视盒子遥控|65728|
|miir.wifispeaker.ir01|音箱遥控|65713|
|miot.clock.mijia|米家App自动化RN的model|5042|
|miwear.headphone.l76c|L76_CN|9443|
|miwear.headphone.l76g|L76_Global|9444|
|mphone.phone.online|小米手机|81306|
|nuwa.robot.minikiwi|小丹机器人|703|
|nuwa.robot.nb1|女媧機器人二代|67100|
|onemore.soundbox.sm001|小米音乐闹钟|205|
|orion.wifispeaker.cm1|小豹AI音箱|668|
|pdwdz.avamp.gf01|派对屋音视频功放控制器|25507|
|rhj.robot.l81|乐天派桌面机器人|77396|
|rokid.robot.alien|Rokid 机器人|297|
|rokid.robot.alien2|Rokid Alien|65560|
|rokid.robot.me|Rokid Me|65793|
|rokid.robot.mini|Rokid Mini|823|
|rokid.robot.panda0|若琪·熊猫|66304|
|rokid.robot.pebble|Rokid 月石|544|
|rokid.robot.pebble2|Rokid Pebble|65561|
|sbar.avamp.sbar|星环智能影音功放|82594|
|szkfd.cooler.k50|KFD手机散热器|34972|
|szkfd.cooler.k58|KFD吸风散热器|37141|
|txdd.wifispeaker.x1|腾讯叮当智能屏|915|
|vidon.avamp.wd2|威动影K一体机C3000|35091|
|wise.wifispeaker.x7|WISE背景音乐情景面板|72004|
|wise1.avamp.wise51|WISE智能5.1影K主机|38283|
|xfocus.wifispeaker.dual|声必可双音源背景音乐|73499|
|xfocus.wifispeaker.m10|声必可安卓中控面板|76986|
|xfocus.wifispeaker.xfos|背景音乐|72233|
|xgimi2.projector.athena|极米智能投影仪 RS 20 Ultra Max|82392|
|xgimi2.projector.g00115|极米智能投影仪 RS30 Ultra Max|84137|
|xgimi2.projector.g0048|极米激光电视 Aura 2|82491|
|xgimi2.projector.g0056|极米激光电视 S6|82524|
|xgimi2.projector.g0058|极米智能投影仪 Play 6|82602|
|xgimi2.projector.g0063|极米智能投影仪 RS 20 Plus|82345|
|xgimi2.projector.g0066|极米智能投影仪 Play 6e|82603|
|xgimi2.projector.g0067|极米智能投影仪 RS  20 Ultra|82343|
|xgimi2.projector.g0070|极米0.78DMD激光HDR电影机|82949|
|xgimi2.projector.g0073|极米智能投影仪 Z6X Pro 三色激光版|82560|
|xgimi2.projector.g0074|极米 家用智能投影 Z6X Pro 三色激光 旗舰版|83003|
|xgimi2.projector.g0076|极米 家用智能投影 Z6X 第五代 高亮版|82657|
|xgimi2.projector.g0077|极米智能投影仪 RS 20 Pro Max|82296|
|xgimi2.projector.g0079|极米智能投影仪 RS 20 Plus 高亮版|82346|
|xgimi2.projector.g0082|极米 家用智能投影 Z9X 4K|82992|
|xgimi2.projector.g0087|极米智能投影仪 RS 20|82754|
|xgimi2.projector.g0088|极米智能投影仪 RS 20 Pro 高亮版|82757|
|xgimi2.projector.g0089|极米智能投影仪 RS 20 Pro Max 高亮版|82758|
|xgimi2.projector.g0095|极米 家用智能投影 Z6X Pro 三色激光 高亮版|82792|
|xgimi2.projector.g0099|极米智能投影仪 RS 20 Ultra Max 高亮版|82868|
|xgimi2.projector.g0100|极米投影 X50 Ultra Max|83766|
|xgimi2.projector.g0104|极米影院级护眼激光电视AURA3 Max|84693|
|xgimi2.projector.g0105|极米影院级护眼激光电视AURA3|84692|
|xgimi2.projector.g0109|极米护眼艺术激光电视 MIRA 4K|84188|
|xgimi2.projector.g0110|极米护眼艺术激光电视 MIRA 4K Pro|84189|
|xgimi2.projector.g0111|极米投影 X50 Ultra|84019|
|xgimi2.projector.g0114|极米智能投影仪 RS30 Ultra|84023|
|xgimi2.projector.g0118|极米 家用智能投影 Z9X 4K 高亮版|83801|
|xgimi2.projector.g0124|极米智能投影仪 RS30 Pro Max|84022|
|xgimi2.projector.g0125|极米智能投影仪 RS30 Pro|84021|
|xgimi2.projector.g0131|极米 家用智能投影 Z6X 第五代 特别版|84046|
|xgimi2.projector.g0149|极米智能投影仪 RS30 高亮版|84729|
|xgimi2.projector.g8202|极米 家用智能投影 Z9X 4K 旗舰版|84042|
|xiaomi.cooler.r02p|小米磁吸散热背夹|21162|
|xiaomi.split_tv.b1|小米电视主机|66461|
|xiaomi.split_tv.v1|小米电视主机|730|
|xiaomi.tv.4kh1|小米电视大师 82吋|68721|
|xiaomi.tv.8kh1|小米电视大师 82吋 至尊纪念版|68673|
|xiaomi.tv.b1|小米电视|66462|
|xiaomi.tv.dso1h1|小米电视 大师77吋 OLED|73439|
|xiaomi.tv.eaffh1|小米电视EA系列|71700|
|xiaomi.tv.eanfv1|小米电视|71699|
|xiaomi.tv.eaprh1|小米电视 EA Pro|9032|
|xiaomi.tv.esh1|小米电视ES系列|72243|
|xiaomi.tv.esprh1|小米电视 ES Pro|75875|
|xiaomi.tv.fsi1|小米全面屏电视|67010|
|xiaomi.tv.fsprov1|小米全面屏电视Pro|66993|
|xiaomi.tv.fsv1|小米全面屏电视|66989|
|xiaomi.tv.h1|小米壁画电视 65英寸|65788|
|xiaomi.tv.i1|小米电视|66464|
|xiaomi.tv.mih1|小米电视|3847|
|xiaomi.tv.mimsh1|小米电视S Pro RGB-Mini LED 2027|35811|
|xiaomi.tv.mitv5h1|小米电视5|66992|
|xiaomi.tv.mitv5proh1|小米电视5Pro|67496|
|xiaomi.tv.mitvsp|Xiaomi TV|1519|
|xiaomi.tv.oledh1|小米电视大师65吋OLED|68674|
|xiaomi.tv.rmaxv1|redmi Max系列|71879|
|xiaomi.tv.rmh1|Redmi电视|69064|
|xiaomi.tv.rmi1|Redmi电视|66990|
|xiaomi.tv.rmv1|Redmi电视|66991|
|xiaomi.tv.tv6h1|小米电视6至尊版|71572|
|xiaomi.tv.v1|小米电视|28|
|xiaomi.tv.z2oh1|小米电视6 oled系列|72244|
|xiaomi.tvbox.b1|小米电视盒子|66463|
|xiaomi.tvbox.i1|小米电视盒子|66465|
|xiaomi.tvbox.v1|小米电视盒子|30|
|xiaomi.wifispeaker.16b|Xiaomi Sound|14437|
|xiaomi.wifispeaker.lx04|小爱触屏音箱|65605|
|xiaomi.wifispeaker.v3|小米网络音箱|65674|
|xiaoxun.robot.v1|小寻儿童电脑|754|
|xiaoya.wifispeaker.ai016|小雅AI图书馆|70139|
|xiaoya.wifispeaker.nano|小雅nano音箱|1804|
|yihe.avamp.yjn01|英嘉尼智能功放|30234|
|yihe.avamp.yybfj|英嘉尼智能影音播放主机|38168|
|yjy.wifispeaker.u9|8寸背景音乐主机|72120|
|yodaar.avamp.i3x|悠达智能音视频功放主机|31155|
|yuemee.wifispeaker.sa2|小米手环 多功能桌搭|25397|
|yuemee.wifispeaker.sa6|小米手环 多功能桌搭|27866|
|yz66.wifispeaker.yz|右转音乐主机|77481|
|zefeng.avamp.amp1|蜗牛SNAIL POWER 8K音视频播控功放|34364|
|zhiee.robot.ad1|百将手指机器人|32319|
|zimi.projector.v1|米家投影仪TYY01ZM|771|
|zw1688.cooler.s1|LWU手机散热器|37937|

### 插座开关

|model|name|pd_id|
|---|---|---:|
|090615.plug.cmp86|PTX 86电量版插座(WIFI)|5766|
|090615.plug.pipa86|噼啪智能开关二三插|71326|
|090615.plug.plus01|智能86插座(WIFI)|66564|
|090615.plug.plus02|智能移动插座(WIFI)|66842|
|090615.plug.plusm2|智能轨道插座|12285|
|090615.remote.akswr1|AK 无线开关单键(PTX)|14608|
|090615.remote.akswr2|AK 无线开关双键(PTX)|14609|
|090615.remote.akswr3|AK 无线开关三键(PTX)|14610|
|090615.remote.btsw1|PTX 无线开关（蓝牙版）|14523|
|090615.remote.desksw|平头熊 X1 调光情景旋钮开关|15944|
|090615.remote.hydesk|皓逸桌面调光情景旋钮无线开关（Pro）|24626|
|090615.remote.mlsw0a|PTX多功能无线开关(MESH)|10371|
|090615.remote.ptxf14|平头熊 F1调光情景开关|32200|
|090615.remote.ptxsd1|平头熊 F1 四键无线开关|27495|
|090615.remote.x1swd|平头熊 F1 四键无线开关(屏显版)|25797|
|090615.remote.x6s4q|X6智能四情景开关(PTX）|9037|
|090615.remote.x6xnsw|PTX 无线情景旋钮开关|11273|
|090615.remote.yk6sw|PTX 六键无线开关|6436|
|090615.switch.09dh1|智能单火开关(MESH) 一开|13487|
|090615.switch.09dh2|智能单火开关(MESH) 二开|13486|
|090615.switch.09dh3|智能单火开关(MESH) 三开|13485|
|090615.switch.aidh1|AI智能单火开关(MESH) 一开|12470|
|090615.switch.aidh2|AI智能单火开关(MESH) 二开|12471|
|090615.switch.aidh3|AI智能单火开关(MESH) 三开|12472|
|090615.switch.aikw1|AE智能开关(MESH) 一开|10674|
|090615.switch.aikw2|AE智能开关(MESH) 二开|10675|
|090615.switch.aikw3|AE智能开关(MESH) 三开|10676|
|090615.switch.aikw4|AE智能开关(MESH) 四开|11720|
|090615.switch.akkw1|AK智能开关(PTX) 一键|11333|
|090615.switch.akkw2|AK智能开关(PTX) 二键|11332|
|090615.switch.akpro1|PTX 超薄美学开关 单键|17943|
|090615.switch.akpro2|PTX 超薄美学开关 双键|17944|
|090615.switch.akpro3|PTX 超薄美学开关 三键|17933|
|090615.switch.akpro4|平头熊超薄美学开关四键 Mesh2.0|21145|
|090615.switch.akps1|平头熊超薄美学开关单键 Mesh2.0|23616|
|090615.switch.akps2|平头熊超薄美学开关双键 Mesh2.0|23617|
|090615.switch.akps3|平头熊超薄美学开关三键 Mesh2.0|23618|
|090615.switch.aksk3|AK智能开关(PTX) 三键|11356|
|090615.switch.akstft|AK智能屏幕开关|15145|
|090615.switch.aku1p|平头熊超薄屏显开关单键 Mesh2.0|27227|
|090615.switch.aku2p|平头熊超薄屏显开关双键 Mesh2.0|27226|
|090615.switch.aku3p|平头熊超薄屏显开关三键 Mesh2.0|27225|
|090615.switch.akult1|平头熊超薄显示屏开关单开 Mesh2.0|19642|
|090615.switch.akult2|平头熊超薄显示屏开关双开 Mesh2.0|19641|
|090615.switch.akult3|平头熊 超薄显示屏开关三开 Mesh2.0|19640|
|090615.switch.akult4|平头熊超薄显示屏开关四开 Mesh2.0|24360|
|090615.switch.azsw01|Azena 蓝牙智能零火版单联开关|5345|
|090615.switch.azsw02|Azena 蓝牙智能零火版双联开关|5346|
|090615.switch.azsw03|Azena 蓝牙智能零火版三联开关|5347|
|090615.switch.cmb01|PTX 双模智能单键开关(WIFI)|4528|
|090615.switch.cmb02|PTX 双模智能双键开关(WIFI)|4527|
|090615.switch.cmb03|PTX 双模智能三键开关(WIFI)|4526|
|090615.switch.cmb21|PTX 双模触摸单键开关(WIFI)|4925|
|090615.switch.cmb22|PTX 双模触摸双键开关(WIFI)|4926|
|090615.switch.cmb23|PTX 双模触摸三键开关(WIFI)|4927|
|090615.switch.fsw2|平头熊F系列精美装饰开关 二开(Mesh2.0)|27584|
|090615.switch.fsw3|平头熊F系列精美装饰开关 三开(Mesh2.0)|27585|
|090615.switch.fsw4|平头熊F系列精美装饰开关 四开(Mesh2.0)|27586|
|090615.switch.ftsw4|平头熊F系列精美表盘定制开关 四开(Mesh2.0)|27981|
|090615.switch.hmb012|H 智能单键开关 (MESH)|4098|
|090615.switch.hmb022|H 智能双键开关 (MESH)|4099|
|090615.switch.hmb032|H 智能三键开关 (MESH)|4100|
|090615.switch.hmsw01|HOMRAY智能开关一键|6795|
|090615.switch.hmsw02|HOMRAY智能开关二键|6796|
|090615.switch.hmsw03|HOMRAY智能开关三键|6797|
|090615.switch.hy3in1|皓逸Smart Home四键开关(屏显版)|26279|
|090615.switch.hytpq5|皓逸超薄中控屏开关Q3Pro (Mesh2.0)|24370|
|090615.switch.hyv1s1|皓逸一键智能开关V1|28582|
|090615.switch.hyv1s2|皓逸二键智能开关V1|28583|
|090615.switch.hyv1s3|皓逸三键智能开关V1|28584|
|090615.switch.ldys4|立德云数4寸中控屏开关|27848|
|090615.switch.mesh01|PTX单火触摸开关一键(MESH)|3489|
|090615.switch.mesh02|PTX单火触摸开关二键(MESH)|3491|
|090615.switch.mesh03|PTX单火触摸开关三键(MESH)|3492|
|090615.switch.meshk1|PTX单火按键开关一键(MESH)|3790|
|090615.switch.meshk2|PTX单火按键开关二键(MESH)|3789|
|090615.switch.meshk3|PTX单火按键开关三键(MESH)|3788|
|090615.switch.mesw1|PTX蓝牙Mesh智能开关 一开|2258|
|090615.switch.mesw2|PTX蓝牙Mesh智能开关 二开|2257|
|090615.switch.mesw3|PTX蓝牙Mesh智能开关 三开|2093|
|090615.switch.mets1|PTX一键智能开关（Mesh）|3880|
|090615.switch.mets2|PTX二键智能开关（Mesh）|3879|
|090615.switch.mets3|PTX三键智能开关（Mesh）|3878|
|090615.switch.mhrsw1|PTX单路蓝牙智能开关模块(Mesh)|2288|
|090615.switch.mhrsw2|PTX双路蓝牙智能开关模块(Mesh)|2289|
|090615.switch.pi16sw|噼啪16路开关通断器|5909|
|090615.switch.piak01|噼啪智能一位开关|68020|
|090615.switch.piak02|噼啪智能二位开关|68021|
|090615.switch.piak03|噼啪智能三位开关|68022|
|090615.switch.ptxpro|平头熊K1 Pro超薄中控屏开关|26686|
|090615.switch.ptxtc1|PTX 智能触摸开关一开(MESH)|4155|
|090615.switch.ptxtc2|PTX 智能触摸开关二开(MESH)|4156|
|090615.switch.ptxtc3|PTX 智能触摸开关三开(MESH)|4157|
|090615.switch.q11pro|平头熊Q1 Pro超薄美学开关 单键|31214|
|090615.switch.q12pro|平头熊Q1 Pro超薄美学开关 双键|31215|
|090615.switch.q13pro|平头熊Q1 Pro超薄美学开关 三键|31216|
|090615.switch.q14max|平头熊Q1 Pro超薄屏显开关 四键|31221|
|090615.switch.q14pro|平头熊Q1 Pro超薄美学开关 四键|31217|
|090615.switch.q1pro|平头熊Q1 Pro超薄中控屏开关|31213|
|090615.switch.q3pro1|皓逸智能开关一开Q3pro(屏显版)|20325|
|090615.switch.q3pro2|皓逸智能开关二开Q3pro(屏显版)|20324|
|090615.switch.q3pro3|皓逸智能开关三开Q3pro(屏显版)|20323|
|090615.switch.qksw01|PTX 智能插卡取电开关(MESH)|4042|
|090615.switch.qksw32|PTX插卡取电开关(WIFI)|4377|
|090615.switch.sk4k|PTX 智能四键开关|6435|
|090615.switch.sk6k|PTX 智能六键开关|5631|
|090615.switch.smb1s1|苏米B1蓝牙Mesh开关（单键）|4072|
|090615.switch.smb1s2|苏米B1蓝牙Mesh开关（二键）|4071|
|090615.switch.smb1s3|苏米B1蓝牙Mesh开关（三键）|4070|
|090615.switch.smbt01|苏米A1蓝牙Mesh开关（单键）|3972|
|090615.switch.smbt02|苏米A1蓝牙Mesh开关（双键）|3973|
|090615.switch.smbt03|苏米A1蓝牙Mesh开关（三键）|3974|
|090615.switch.switch01|一键智能开关(WIFI)|66456|
|090615.switch.switch02|二键智能开关(WIFI)|66457|
|090615.switch.switch03|三键智能开关(WIFI)|66075|
|090615.switch.tftcmb|旋钮智能开关|5797|
|090615.switch.ultra1|平头熊Q1 Pro超薄屏显开关 单键|31218|
|090615.switch.ultra2|平头熊Q1 Pro超薄屏显开关 双键|31219|
|090615.switch.ultra3|平头熊Q1 Pro超薄屏显开关 三键|31220|
|090615.switch.wtmk01|沃铁智能单键开关|26107|
|090615.switch.wtmk02|沃铁智能双键开关|26108|
|090615.switch.wtmk03|沃铁智能三键开关|26109|
|090615.switch.wtmp4|沃铁智能中控屏开关 MP4 ultra|26040|
|090615.switch.x1tp|智能屏幕开关(PTX)|19083|
|090615.switch.x1tpm|平头熊超薄中控屏开关 Mesh2.0|21667|
|090615.switch.x6gr1|GR谷雨智能一键开关|12193|
|090615.switch.x6gr2|GR谷雨智能二键开关|12194|
|090615.switch.x6gr3|GR谷雨智能三键开关|12195|
|090615.switch.x6gr4|GR谷雨智能四键开关|12196|
|090615.switch.x6gr6|GR谷雨智能六键开关|12197|
|090615.switch.x6hy1|皓逸智能单键开关|11818|
|090615.switch.x6hy2|皓逸智能双键开关|11820|
|090615.switch.x6hy3|皓逸智能三键开关|11821|
|090615.switch.x6hy4|皓逸智能四键开关|11824|
|090615.switch.x6hy6|皓逸智能六键开关|11825|
|090615.switch.x6kw1|PTX智能一键开关 (X6)|11652|
|090615.switch.x6kw2|PTX智能二键开关 (X6)|11653|
|090615.switch.x6kw3|PTX智能三键开关 (X6)|11654|
|090615.switch.x6kw4|PTX 智能四键开关(X6)|15135|
|090615.switch.x6ntft|X6智能旋钮屏开关(PTX)|14174|
|090615.switch.x6se1|MAXBORN 智能单键开关|11826|
|090615.switch.x6se2|MAXBORN 智能双键开关|11827|
|090615.switch.x6se3|MAXBORN 智能三键开关|11828|
|090615.switch.x6tppr|K1高清中控屏开关 (PTX)|19847|
|090615.switch.x6wtft|X6智能中控屏开关 (WIFI)|12133|
|090615.switch.x7sw2|X7 双键智能开关 (PTX)|14443|
|090615.switch.x7sw3|X7 三键智能开关 (PTX)|14441|
|090615.switch.x7sw4|X7 四键智能开关 (PTX)|14444|
|090615.switch.xswitch01|PTX一键开关(WIFI)|66952|
|090615.switch.xswitch02|PTX二键开关(WIFI)|66502|
|090615.switch.xswitch03|PTX三键开关(WIFI)|66951|
|180.plug.plug0001|Ai-Thinker 智能插座|66735|
|3399xx.remote.cekikg|CEKI 智能无线开关|30845|
|50blue.switch.zbtdq|ZDDBOO Mesh2.0通断器|35109|
|50blue.switch.zddtdq|ZDDBOO WiFi通断器|35526|
|704719.switch.sw1b01|简顿智能开关单键|40128|
|704719.switch.sw2b01|简顿智能开关双键|40129|
|704719.switch.sw3b01|简顿智能开关三键|40130|
|704719.switch.sw4b01|简顿智能开关四键|40187|
|722231.plug.001|TEP国际电工智能轨道插座|29529|
|722231.switch.m3px01|TEP国际电工M3系列智能一键屏显开关|36502|
|722231.switch.m3px02|TEP国际电工M3系列智能二键屏显开关|36503|
|722231.switch.m3px03|TEP国际电工M3系列智能三键屏显开关|36504|
|722231.switch.m3sw01|TEP国际电工M1系列智能一键开关|36745|
|722231.switch.m3sw02|TEP国际电工M1系列智能二键开关|36746|
|722231.switch.m3sw03|TEP国际电工M1系列智能三键开关|36747|
|722231.switch.m3sw04|TEP国际电工M1系列智能四键开关|36748|
|722231.switch.sw1a01|TEP国际电工S7系列智能一键开关|32966|
|722231.switch.sw1b01|TEP国际电工M8系列智能一键开关|32970|
|722231.switch.sw2a01|TEP国际电工S7系列智能二键开关|32968|
|722231.switch.sw2b01|TEP国际电工M8系列智能二键开关|32972|
|722231.switch.sw3a01|TEP国际电工S7系列智能三键开关|32969|
|722231.switch.sw3b01|TEP国际电工M8系列智能三键开关|32973|
|722231.switch.sw4a01|TEP国际电工S7系列智能四键开关|34503|
|722231.switch.sw4b01|TEP国际电工M8系列智能四键开关|32974|
|888888.switch.sbkg1|米舍超薄美学单键开关(Mesh2.0)|30016|
|888888.switch.sbkg2|米舍超薄美学双键开关(Mesh2.0)|30017|
|888888.switch.sbkg3|米舍超薄美学三键开关(Mesh2.0)|30018|
|888888.switch.sbkg4|米舍超薄美学多键开关(Mesh2.0)|30019|
|abhome.switch.sw1a01|SASELAN情景智能开关一开|32151|
|abhome.switch.sw2a01|SASELAN情景智能开关二开|27325|
|abhome.switch.sw3a01|SASELAN情景智能开关三开|27326|
|abhome.switch.sw4a01|SASELAN情景智能开关四开|27327|
|adl001.plug.itcs|奥多朗智能轨道转换插座|20847|
|ahorro.switch.an1k|ahorro奥能蓝牙一开|22560|
|ahorro.switch.an2k|ahorro奥能蓝牙二开|22562|
|ahorro.switch.an3k|ahorro奥能蓝牙三开|22563|
|ahorro.switch.an4k|ahorro奥能蓝牙四开|22564|
|aikeji.switch.sw0a02|AKG智能通断器3.0|40824|
|aikeji.switch.sw1a01|AKG智能开关-G系列1开|38607|
|aikeji.switch.sw2a01|AKG智能开关-G系列2开|38608|
|aikeji.switch.sw3a01|AKG智能开关-G系列3开|38609|
|aikeji.switch.sw4a01|AKG智能开关-G系列4开|38610|
|ailol.remote.ts4|智有范F2智能旋钮遥控器|18250|
|ailol.switch.sw1a01|智有范 2键智能开关|16533|
|ailol.switch.sw2a01|智有范 4键智能开关|16534|
|ailol.switch.sw2b01|智有范2键智能开关M1|28102|
|ailol.switch.sw3a01|智有范 6键智能开关|16535|
|ailol.switch.sw4a01|智有范 8键智能开关|16536|
|ailol.switch.sw4b01|智有范4键智能开关M1|28103|
|ailol.switch.sw6b01|智有范6键智能开关M1|28104|
|aizbot.switch.amtdq|Aiasst智能通断器（Mesh2.0）|34454|
|aizbot.switch.awtdq|Aiasst智能通断器（Wi-Fi）|34456|
|aizbot.switch.zqkg1|智秋1路通断器（Mesh2.0）|31280|
|aizbot.switch.zqkg2|智秋2路通断器（Mesh2.0）|31279|
|aizbot.switch.zqkg4|智秋4路通断器（Mesh2.0）|31278|
|al425.remote.sw1a01|AWS 蓝牙智能无线旋钮开关|25818|
|alight.switch.azkg1|光缓智能开关Pro 单键|37867|
|alight.switch.azkg2|光缓智能开关Pro 双键|37866|
|alight.switch.azkg3|光缓智能开关Pro 三键|37865|
|alight.switch.azkg4|光缓智能开关Pro 四键|37864|
|amoi.switch.bln02|H.E.P-夏新智能二键开关|30496|
|amoi.switch.bln03|H.E.P-夏新智能三键开关|30497|
|amoi.switch.bln04|H.E.P-夏新智能四键开关|30498|
|andi.switch.sw0a02|ZXWL智能双路通断器3.0|39828|
|andi.switch.sw0a03|ZXWL智能通断器3.0|40755|
|andi.switch.sw1a01|ZXWL智能开关-S系列1开|30549|
|andi.switch.sw2a01|ZXWL智能开关-S系列2开|30548|
|andi.switch.sw3a01|ZXWL智能开关-S系列3开|30547|
|andi.switch.sw4a01|ZXWL智能开关-S系列4开|30546|
|andi.switch.sw4b01|ZXWL屏显智能开关-P系列4开|30541|
|ax01.switch.bln31|AX单火智能一键开关|27759|
|ax01.switch.bln32|AX单火智能二键开关|27760|
|ax01.switch.bln33|AX单火智能三键开关|27761|
|ax01.switch.px01|AX智能屏显一键开关|32270|
|ax01.switch.px02|AX智能屏显二键开关|32271|
|ax01.switch.px03|AX智能屏显三键开关|32272|
|ax01.switch.sw0a02|AX智能通断器|40537|
|ax01.switch.sw1a01|AX智能一键开关|27335|
|ax01.switch.sw1a04|AX智联场景开关屏|35179|
|ax01.switch.sw1b01|安想S1系列零火智能一键开关|30277|
|ax01.switch.sw1c01|安想S7系列智能开关一开|30532|
|ax01.switch.sw1d01|AX智联一键开关（田字版）|34795|
|ax01.switch.sw1e01|AX智联一键开关（竖版）|34827|
|ax01.switch.sw1h01|AX智系列一键开关|39844|
|ax01.switch.sw2a01|AX智能二键开关|27336|
|ax01.switch.sw2b01|安想S1系列零火智能二键开关|30278|
|ax01.switch.sw2c01|安想S7系列智能开关二开|30531|
|ax01.switch.sw2d01|AX智联二键开关（田字版）|34796|
|ax01.switch.sw2e01|AX智联二键开关（竖版）|34826|
|ax01.switch.sw2h01|AX智系列二键开关|39845|
|ax01.switch.sw3a01|AX智能三键开关|27337|
|ax01.switch.sw3b01|安想S1系列零火智能三键开关|30279|
|ax01.switch.sw3c01|安想S7系列智能开关三开|30530|
|ax01.switch.sw3d01|AX智联三键开关（田字版）|34797|
|ax01.switch.sw3e01|AX智联三键开关（竖版）|34825|
|ax01.switch.sw3h01|AX智系列三键开关|39846|
|ax01.switch.sw4a01|AX智能四键开关|27338|
|ax01.switch.sw4b01|安想S1系列零火智能四键开关|30280|
|ax01.switch.sw4c01|安想S7系列智能开关四开|34019|
|ax01.switch.sw4d01|AX智联四键开关（田字版）|34798|
|ax01.switch.sw4e02|AX智联四键开关（竖版）|34824|
|ax01.switch.sw4g01|AX智联彩色屏显开关|37431|
|ax01.switch.sw4h01|AX智系列四键开关|39847|
|axzn.plug.s2w|NIOT 智能（温控）转换插座|38496|
|axzn.plug.s3|NIOT 智能（计量）转换插座|29384|
|axzn.switch.r3|安心R3智能断路器|15191|
|babai.plug.sk01a|Babuy Wi-Fi 智能插座|70225|
|babai.plug.sk86a|Babuy 二三极智能插座|70226|
|babai.switch.201m|Ai 智能一键Mesh开关|6514|
|babai.switch.201ml|Ai 智能一键Mesh开关（单火版）|7219|
|babai.switch.201s|Ai 智能一键开关（WiFi双模）|6098|
|babai.switch.202m|Ai 智能二键Mesh开关|6528|
|babai.switch.202ml|Ai 智能二键Mesh开关（单火版）|7220|
|babai.switch.202s|Ai 智能二键开关（WiFi双模）|6099|
|babai.switch.203m|Ai 智能三键Mesh开关|6529|
|babai.switch.203ml|Ai 智能三键Mesh开关（单火版）|7221|
|babai.switch.203s|Ai 智能三键开关（WiFi双模）|6100|
|babai.switch.301m|Ai 智能一键开关(MESH零火)|11567|
|babai.switch.301ml|Ai 智能一键开关(MESH单火)|11572|
|babai.switch.302m|Ai 智能二键开关(MESH零火)|11568|
|babai.switch.302ml|Ai 智能二键开关(MESH单火)|11574|
|babai.switch.303m|Ai 智能三键开关(MESH零火)|11569|
|babai.switch.303ml|Ai 智能三键开关(MESH单火)|11575|
|babai.switch.304m|Ai 智能四键开关(MESH零火)|11570|
|babai.switch.304ml|Ai 智能四键开关(MESH单火)|11576|
|babai.switch.308m|Ai 智能八键开关(MESH零火)|11571|
|babai.switch.308ml|Ai 智能八键开关(MESH单火)|11577|
|babai.switch.ah1ml|ahorro奥能蓝牙1开|14870|
|babai.switch.ah2m|ahorro奥能蓝牙2开|14871|
|babai.switch.ah3m|ahorro奥能蓝牙3开|14872|
|babai.switch.ah4m|ahorro奥能蓝牙4开|14873|
|babai.switch.bb101s|Ai 智能一键WiFi开关|68739|
|babai.switch.bb102s|Ai 智能二键WiFi开关|68738|
|babai.switch.bb103s|Ai 智能三键WiFi开关|68497|
|babai.switch.th01a|ThoughtHome智能通断器|70987|
|babai.switch.th01m|Ai 智能通断器(MESH)|12601|
|bean.switch.bl01|单键开关-单火Mesh版|9609|
|bean.switch.bl02|双键开关-单火Mesh版|9610|
|bean.switch.bl03|三键开关-单火Mesh版|9611|
|bean.switch.bl04|四键单火开关V2-Mesh版|14918|
|bean.switch.bln01|单键开关-零火Mesh版|9612|
|bean.switch.bln02|双键开关-零火Mesh版|9613|
|bean.switch.bln03|三键开关-零火Mesh版|9614|
|bean.switch.bln04|四键开关-零火Mesh版|10147|
|bean.switch.bln31|智能一键开关S2-Mesh版|18112|
|bean.switch.bln32|智能二键开关S2-Mesh版|18585|
|bean.switch.bln33|智能三键开关S2-Mesh版|18586|
|bean.switch.bln34|智能四键开关S2-Mesh版|18588|
|bean.switch.bln36|智能六键开关S2-Mesh版|20006|
|bean.switch.bln51|YM一键屏显开关Z3|22263|
|bean.switch.bln52|YM二键屏显开关Z3|22262|
|bean.switch.bln54|YM四键屏显开关Z3|22240|
|bean.switch.blns1|智能一键开关S1-Mesh版|18577|
|bean.switch.blns2|智能二键开关S1-Mesh版|18578|
|bean.switch.blns3|智能三键开关S1-Mesh版|18579|
|bean.switch.bpns3|YM三键屏显开关Z3|22123|
|bean.switch.bpns6|YM六键屏显开关Z3|22117|
|beiyun.switch.250c|seebest智能调光器（蓝牙Mesh版）|5795|
|belede.remote.sw1b03|贝朗德情景无线开关三键|34897|
|belede.remote.sw1b06|贝朗德情景无线开关六键|34899|
|belede.switch.s9ol1k|贝朗德超薄屏显智能一键开关|29512|
|belede.switch.s9ol2k|贝朗德超薄屏显智能二键开关|29513|
|belede.switch.s9ol3k|贝朗德超薄屏显智能三键开关|29514|
|belede.switch.sw0a01|贝朗德智能通断器|30506|
|belede.switch.sw1a01|贝朗德情景智能一键开关|28720|
|belede.switch.sw1a02|贝朗德M17-OL屏显一键开关|30104|
|belede.switch.sw1b01|贝朗德超薄智能一键开关|30237|
|belede.switch.sw1b11|贝朗德S9超薄智能一键开关|39624|
|belede.switch.sw1c01|贝朗德智能单火一键开关|30273|
|belede.switch.sw1d01|贝朗德-M15屏显二键开关|30390|
|belede.switch.sw1d02|贝朗德-M15屏显三键开关|30391|
|belede.switch.sw1d03|贝朗德-M15屏显四键开关|30392|
|belede.switch.sw1e01|贝朗德智能一键开关|32112|
|belede.switch.sw2a01|贝朗德情景智能二键开关|28721|
|belede.switch.sw2a02|贝朗德M17-OL屏显二键开关|30105|
|belede.switch.sw2b01|贝朗德超薄智能二键开关|30238|
|belede.switch.sw2b11|贝朗德S9超薄智能二键开关|39623|
|belede.switch.sw2c01|贝朗德智能单火二键开关|30274|
|belede.switch.sw2e01|贝朗德智能二键开关|32113|
|belede.switch.sw3a01|贝朗德情景智能三键开关|28722|
|belede.switch.sw3a02|贝朗德M17-OL屏显三键开关|30106|
|belede.switch.sw3b01|贝朗德超薄智能三键开关|30239|
|belede.switch.sw3b11|贝朗德S9超薄智能三键开关|39622|
|belede.switch.sw3c01|贝朗德智能单火三键开关|30275|
|belede.switch.sw3e02|贝朗德智能三键开关|33092|
|belede.switch.sw4a01|贝朗德情景智能四键开关|28723|
|belede.switch.sw4a02|贝朗德M17-OL屏显四键开关|30108|
|belede.switch.sw4a04|贝朗德S9-TFMAX彩屏智能四键开关|37457|
|belede.switch.sw4a05|贝朗德S9-TFMAX彩屏智能三键开关|39305|
|belede.switch.sw4a06|贝朗德S9-TFMAX彩屏智能二键开关|39306|
|belede.switch.sw4a07|贝朗德S9-TFMAX彩屏智能一键开关|39307|
|belede.switch.sw4b01|贝朗德S9超薄智能四键开关|39064|
|belede.switch.sw4c01|贝朗德智能单火四键开关|30276|
|belede.switch.sw4c02|贝朗德屏显智能四键开关|30285|
|belede.switch.sw4e01|贝朗德智能四键开关|32115|
|belede.switch.sw8a01|贝朗德八键智能情景开关|32847|
|bellzn.switch.blkg1|贝邻智能一键复合开关|39031|
|bellzn.switch.blkg2|贝邻智能二键复合开关|39032|
|bellzn.switch.blkg3|贝邻智能三键复合开关|39033|
|bellzn.switch.blkg4|贝邻智能四键复合开关|39034|
|bjkcz.remote.kczk1s|科创者K1四键情景无线贴屏显版|29648|
|bjkcz.switch.kczk11|科创者K1 超薄智能开关一键 2.0|29789|
|bjkcz.switch.kczk12|科创者K1 超薄智能开关二键 2.0|29790|
|bjkcz.switch.kczk13|科创者K1 Ultra 超薄中控屏开关2.0|29788|
|bjkcz.switch.kczk14|科创者 K1 Pro 超薄四键显示屏开关2.0|29786|
|bjkcz.switch.kczk33|科创者K1 超薄智能开关三键 2.0|29792|
|bjkcz.switch.kczk44|科创者K1 超薄智能开关四键 2.0|29793|
|bkxh.switch.sw1a01|小海·见晓零火单键智能开关|38416|
|bkxh.switch.sw2a01|小海·见晓零火双键智能开关|38417|
|bkxh.switch.sw3a01|小海·见晓零火三键智能开关|38418|
|bmjzn.switch.csdkg1|创视多智能一路开关（Mesh2.0）|31885|
|bmjzn.switch.csdkg2|创视多智能二路开关（Mesh2.0）|31891|
|bmjzn.switch.csdkg3|创视多智能三路开关（Mesh2.0）|31144|
|bmjzn.switch.csdkg4|创视多智能四路开关（Mesh2.0）|31895|
|bnen1.switch.sw1b01|百能智联一键开关(竖版)|38151|
|bnen1.switch.sw2b01|百能智联二键开关(竖版)|38154|
|bnen1.switch.sw3b01|百能智联三键开关(竖版)|38155|
|bnen1.switch.sw4b01|百能智联四键开关(竖版)|38156|
|boade.switch.sw1a01|MINFAN 一位智能开关|36032|
|boade.switch.sw2a01|MINFAN 二位智能开关|36033|
|boade.switch.sw3a01|MINFAN 三位智能开关|36034|
|boade.switch.sw3a03|MINFAN 智能全面屏开关|35877|
|boade.switch.sw4a01|MINFAN 四位智能开关|36035|
|boerg.plug.begtdq|博尔高智能通断器（Mesh）|30856|
|boerg.switch.begmtd|博尔高通断器V9（Mesh2.0）|34446|
|boerg.switch.begwtd|博尔高智能直连通断器（WiFi）|34455|
|boerg.switch.tdq3|博尔高智能通断器Mesh版|31586|
|boerg.switch.tdqm1|博尔高蓝牙MESH智能通断器|38424|
|bogin8.switch.sw1a01|柏晶一键智能开关|28860|
|bogin8.switch.sw2a01|柏晶二键智能开关|28861|
|bogin8.switch.sw3a01|柏晶三键智能开关|28862|
|bogin8.switch.sw4a01|柏晶四键智能开关|28863|
|bogin8.switch.sw4b01|柏晶智能四键屏显开关|31102|
|broway.switch.bemkg1|博尔美屏显智能开关(一位)|37063|
|broway.switch.bemkg2|博尔美屏显智能开关(二位)|37065|
|broway.switch.bemkg3|博尔美屏显智能开关(三位)|37066|
|broway.switch.sw1|博尔美智能开关(一位)|30870|
|broway.switch.sw2|博尔美智能开关(二位)|27028|
|broway.switch.sw3|博尔美智能开关(三位)|30869|
|broway.switch.sw4|博尔美智能开关(四位)|27027|
|brrx.switch.qst1c1|潜水艇智能墙壁开关1控1|7042|
|brrx.switch.qst1c2|潜水艇智能墙壁开关1控2|7041|
|brrx.switch.qst1c3|潜水艇智能墙壁开关1控3|7039|
|btzn.controller.v1|比特场景开关|71629|
|btzn.switch.1key|比特单键弱电开关|68692|
|btzn.switch.2key|比特双键弱电开关|68847|
|btzn.switch.4key|比特四键弱电开关|68846|
|btzn.switch.bh8b1|bittel比特开关1键（蓝牙mesh）|7787|
|btzn.switch.bh8b2|bittel比特开关2键（蓝牙mesh）|7788|
|btzn.switch.bh8b3|bittel比特开关3键（蓝牙mesh）|7789|
|btzn.switch.cardv1|比特插卡取电开关|70224|
|bull.remote.gts115|公牛智能一位无线开关|32421|
|bull.remote.gts215|公牛智能二位无线开关|32129|
|bull.remote.gts315|公牛智能三位无线开关|31684|
|bull.remote.s115y|公牛G55智能一位无线开关|7554|
|bull.remote.s215y|公牛G55智能二位无线开关|7553|
|bull.remote.s315y|公牛G55智能三位无线开关|7552|
|bull.remote.ts411a|公牛智能四位零火情景开关|32529|
|bull.switch.gts111|公牛智能一位单零火开关|31488|
|bull.switch.gts211|公牛智能二位单零火开关|31475|
|bull.switch.gts311|公牛智能三位单零火开关|31461|
|bull.switch.gts411|公牛智能四位单零火开关|37810|
|bull.switch.s01k01|公牛智能一位零火开关S01|35839|
|bull.switch.s01k02|公牛智能二位零火开关S01|35840|
|bull.switch.s01k03|公牛智能三位零火开关S01|35841|
|bull.switch.s01k04|公牛智能四位零火开关S01|35842|
|bull.switch.s02k01|公牛智能一位零火开关S02|37329|
|bull.switch.s02k02|公牛智能二位零火开关S02|37330|
|bull.switch.s02k03|公牛智能三位零火开关S02|37331|
|bull.switch.s02k04|公牛智能四位零火开关S02|37332|
|bull.switch.s112y|公牛智能一位开关（单火）|7535|
|bull.switch.s212y|公牛智能二位开关（单火）|7534|
|bull.switch.s312y|公牛智能三位开关（单火）|7529|
|bull.switch.ts111a|公牛智能一位零火开关|32088|
|bull.switch.ts211a|公牛智能二位零火开关|32087|
|bull.switch.ts311a|公牛智能三位零火开关|32086|
|bull.switch.ts411b|公牛智能四位零火开关|37862|
|bull.switch.x01d01|公牛智能调光旋钮屏零火开关X系列|35868|
|bull.switch.x01k04|公牛智能四位带屏显零火开关X系列|36323|
|bull.switch.x01k1s|公牛智能一位带屏显零火开关X系列|37655|
|bull.switch.x01k2s|公牛智能二位带屏显零火开关X系列|37654|
|bull.switch.x01k3s|公牛智能三位带屏显零火开关X系列|37174|
|bull.switch.x01t1s|公牛智能四寸屏零火开关X系列|37651|
|bymiot.controller.ctlv1|未来居调光旋钮（冷暖）|78481|
|bymiot.controller.lumv1|未来居调光旋钮（亮度）|78480|
|bymiot.controller.v1|未来居背景音乐控制器|78379|
|bymiot.cs.sensor|未来居有线弱电插卡取电|76570|
|bymiot.cs.switch|未来居有线强电插卡取电|76571|
|bymiot.cs.wlv1|未来居无线强电插卡取电|71768|
|bymiot.cs.wlv2|未来居轻连插卡取电|16918|
|bymiot.cs.wlv3|未来居轻连强电插卡取电（Mesh 2.0）|27159|
|bymiot.plug.wlv1|未来居无线墙壁插座（电流检测）|73469|
|bymiot.relay.wlv1|未来居无线干接点输出模块|76510|
|bymiot.remote.1kwlv1|未来居无线单键场景开关|75034|
|bymiot.remote.2kwlv1|未来居无线双键场景开关|75033|
|bymiot.remote.3kwlv1|未来居无线三键场景开关|75032|
|bymiot.remote.4kwlv2|未来居无线四键场景开关|75028|
|bymiot.remote.6kwlv1|未来居无线六键场景开关|75007|
|bymiot.remote.lockv2|未来居控锁器|75197|
|bymiot.remote.wl|未来居面板|78829|
|bymiot.switch.1keyv1|未来居单键强电开关|67695|
|bymiot.switch.1kwls2|未来居单(零)火兼容智能开关(单键)|19783|
|bymiot.switch.1kwls3|未来居零火智能开关(单键)|20341|
|bymiot.switch.1kwls5|未来居S9Ultra彩屏屏显开关单键（Mesh 2.0）|36758|
|bymiot.switch.1kwls6|未来居智能开关一键开关（Mesh 2.0）|36762|
|bymiot.switch.1kwlv1|未来居轻连单键强电开关|3898|
|bymiot.switch.1kwlv2|未来居单键强电无线开关|71752|
|bymiot.switch.1kwlv3|知或居智能开关Mesh2.0（一键）|24848|
|bymiot.switch.1kwlv4|未来居智能开关Mesh2.0（一键）|25487|
|bymiot.switch.2keyv1|未来居双键强电开关|67697|
|bymiot.switch.2kwls2|未来居单(零)火兼容智能开关(双键)|19784|
|bymiot.switch.2kwls3|未来居零火智能开关(双键)|20342|
|bymiot.switch.2kwls5|未来居S9Ultra彩屏屏显开关双键（Mesh 2.0）|36759|
|bymiot.switch.2kwls6|未来居智能开关双键开关（Mesh 2.0）|36763|
|bymiot.switch.2kwlv1|未来居轻连双键强电开关|3897|
|bymiot.switch.2kwlv2|未来居双键强电无线开关|71751|
|bymiot.switch.2kwlv3|知或居智能开关Mesh2.0（二键）|24849|
|bymiot.switch.2kwlv4|未来居智能开关Mesh2.0（二键）|25488|
|bymiot.switch.3keyv1|未来居三键强电开关|67868|
|bymiot.switch.3kwls2|未来居单(零)火兼容智能开关(三键)|19785|
|bymiot.switch.3kwls3|未来居零火智能开关(三键)|20343|
|bymiot.switch.3kwls5|未来居S9Ultra彩屏屏显开关三键（Mesh 2.0）|36760|
|bymiot.switch.3kwls6|未来居智能开关三键开关（Mesh 2.0）|36764|
|bymiot.switch.3kwlv1|未来居轻连三键强电开关|3896|
|bymiot.switch.3kwlv2|未来居三键强电无线开关|71750|
|bymiot.switch.3kwlv3|知或居智能开关Mesh2.0（三键）|24850|
|bymiot.switch.3kwlv4|未来居智能开关Mesh2.0（三键）|25489|
|bymiot.switch.4keyv1|未来居四键强电开关|67698|
|bymiot.switch.4kwls2|未来居单(零)火兼容智能开关(四键)|19786|
|bymiot.switch.4kwls3|未来居零火智能开关(四键)|20344|
|bymiot.switch.4kwls5|未来居S9Ultra彩屏屏显开关四键（Mesh2.0）|36761|
|bymiot.switch.4kwls6|未来居智能开关四键开关（Mesh 2.0）|36765|
|bymiot.switch.4kwlv1|未来居轻连四键强电开关|3218|
|bymiot.switch.4kwlv2|未来居四键强电无线开关|71749|
|bymiot.switch.4kwlv3|知或居智能开关Mesh2.0（四键）|24851|
|bymiot.switch.4kwlv4|未来居智能开关Mesh2.0（四键）|25490|
|bymiot.switch.6keyv1|未来居六键强电开关|67699|
|bymiot.switch.6kwlv1|未来居轻连六键强电开关|3893|
|bymiot.switch.6kwlv2|未来居六键强电无线开关|71747|
|bymiot.switch.nad1bs|Nano SubDevice -1 Button Switch|74710|
|bymiot.switch.nad2bs|Nano SubDevice -2 Button Switch|74768|
|bymiot.switch.nad3bs|Nano SubDevice -3 Button Switch|74769|
|bymiot.switch.nad4bs|Nano SubDevice -4 Button Switch|74770|
|bymiot.switch.plcv1|未来居PLC智能四键开关面板|81735|
|bymiot.switch.px01|未来居超薄屏显开关单键 Mesh2.0|36065|
|bymiot.switch.px02|未来居超薄屏显开关双键 Mesh2.0|36066|
|bymiot.switch.px03|未来居超薄屏显开关三键 Mesh2.0|36067|
|bymiot.switch.v2|未来居有线单路灯控器|81171|
|bymiot.switch.wlv2|未来居PLC智能八键开关面板|82223|
|bymiot.switch.wlv3|知或居智能屏幕开关|28082|
|cchome.switch.86l1v1|倍增墙壁开关单键版|68310|
|cchome.switch.86l2v1|倍增墙壁开关双键版|68311|
|cchome.switch.86l3v1|倍增墙壁开关三键版|71914|
|cd168.switch.cdtdq|YETFIF智能通断器|37268|
|cddz.plug.pc01m|Jiuhao电脑开机卡(MESH)|15439|
|cddz.plug.pc01w|Jiuhao电脑开机卡|14914|
|cddz.plug.pc03w|Jiuhao电脑开机卡Pro (WiFi)|26771|
|cddz.plug.pc04m|Jiuhao电脑开机卡Pro (Mesh2.0)|29928|
|cddz.remote.cdwx1|Jiuhao一键无线开关|35330|
|cddz.remote.cdwx8|Jiuhao八键无线开关|35331|
|cddz.switch.cdmtdq|Jiuhao智能通断器V9（Mesh 2.0）|34415|
|cddz.switch.cdtdq|Jiuhao智能通断器V9（WiFi）|35405|
|cddz.switch.jhicw|Jiuhao智能开关|22673|
|cdn.remote.c4m3|西顿舍见PLC场景面板(四键)|77531|
|cdn.remote.c6m3|西顿舍见PLC场景面板(六键)|77532|
|cdn.remote.ts01|西顿舍见旋钮无线开关|31014|
|cdn.remote.x1md2|舍见二键场景开关|7666|
|cdn.remote.x1md3|舍见三键场景开关|7667|
|cdn.switch.1dlhjr|西顿单零火兼容开关M2（一开）|28711|
|cdn.switch.1knm3|西顿智能零火开关M2（一开）|29987|
|cdn.switch.2klnm3|西顿智能零火开关M2（二开）|29986|
|cdn.switch.3klnm3|西顿智能零火开关M2（三开）|29985|
|cdn.switch.4dlhjr|西顿单零火兼容开关M2（四开）|28712|
|cdn.switch.4klnm3|西顿智能零火开关M2（四开）|29984|
|cdn.switch.c4k2lc|西顿智能屏显开关M6（二开）|24159|
|cdn.switch.c4k3lc|西顿智能屏显开关M6（三开）|24160|
|cdn.switch.c4k4lc|西顿智能屏显开关M6（四开）|24161|
|cdn.switch.c4k4p7|西顿PLC屏显开关M6（四开）|82435|
|cdn.switch.c6k3yp|西顿PLC六键圆屏开关M6|82473|
|cdn.switch.dlhjr2|西顿单零火兼容开关M2 (二开)|27627|
|cdn.switch.dlhjr3|西顿单零火兼容开关M2 (三开)|27628|
|cdn.switch.fh002|西顿舍见PLC复合面板(四键)|80169|
|cdn.switch.fh003|西顿舍见PLC复合面板(六键)|80168|
|cdn.switch.m2ak1|西顿单键智能零火开关M2air|39854|
|cdn.switch.m2ak2|西顿二键智能零火开关M2air|40076|
|cdn.switch.m2ak3|西顿三键智能零火开关M2air|40077|
|cdn.switch.m2ak4|西顿四键智能零火开关M2air|40078|
|cdn.switch.m6ak1|西顿单键智能屏显开关M6air|39849|
|cdn.switch.m6ak2|西顿二键智能屏显开关M6air|39855|
|cdn.switch.m6ak3|西顿三键智能屏显开关M6air|39851|
|cdn.switch.m6ak4|西顿四键智能屏显开关M6air|39852|
|cdn.switch.m8k2|西顿智能屏显开关M8（二开）|30797|
|cdn.switch.m8k3|西顿智能屏显开关M8（三开）|30798|
|cdn.switch.m8k4|西顿智能屏显开关M8（四开）|30799|
|cdn.switch.m8yp4|西顿智能圆屏开关M8（四开）|30796|
|cdn.switch.x1msl2|舍见智能墙壁开关（二键）|9595|
|cdn.switch.x1msl3|舍见智能墙壁开关（三键）|9594|
|cdn.switch.x6|六键复合调光面板|15653|
|cdn.switch.znypkg|西顿智能圆屏多功能开关M6(六键）|27624|
|cdn.switch.znzkp4|西顿智慧屏开关M6|27625|
|cgzn.switch.cgwt01|初冠智能一键WiFi开关|4584|
|chida.switch.bln31|炽达智能开关 (一开零火版)|22147|
|chida.switch.bln32|炽达智能开关 (二开零火版)|22148|
|chida.switch.bln33|炽达智能开关 (三开零火版)|22149|
|chida.switch.bln34|炽达智能开关 (四开零火版)|22150|
|chitco.switch.sw1a01|CHITCO智能开关(一开)|30838|
|chitco.switch.sw2a01|CHITCO智能开关(二开)|30839|
|chitco.switch.sw3a01|CHITCO智能开关(三开)|30840|
|chitco.switch.sw4a01|CHITCO智能开关(四开)|30841|
|chnt.switch.bln01|正泰智能开关（一位零火）|33319|
|chnt.switch.bln02|正泰智能开关（二位零火）|33320|
|chnt.switch.bln03|正泰智能开关（三位零火）|33321|
|chnt.switch.bln04|正泰智能开关（四位零火）|33322|
|chnt.switch.bln05|正泰X5E一位智能开关|33753|
|chnt.switch.bln06|正泰X5E二位智能开关|33754|
|chnt.switch.bln07|正泰X5E三位智能开关|33755|
|chnt.switch.cadlh1|正泰Z1一位智能开关(单零火)|36742|
|chnt.switch.cadlh2|正泰Z1二位智能开关(单零火)|36743|
|chnt.switch.cadlh3|正泰Z1三位智能开关(单零火)|36744|
|chnt.switch.calh01|正泰Z1一位智能开关|36736|
|chnt.switch.calh02|正泰Z1二位智能开关|36737|
|chnt.switch.calh03|正泰Z1三位智能开关|36738|
|chnt.switch.calh04|正泰Z1四位智能开关|36739|
|chuangmi.plug.212a01|米家智能插座2 蓝牙网关版|2451|
|chuangmi.plug.hmi208|米家智能插座蓝牙网关版|1293|
|chuangmi.plug.m3|小米米家智能插座WiFi版|763|
|chuangmi.plug.v1|小米智能插座|14|
|chuangmi.plug.v2|小米智能插座基础版(已失效)|99|
|chuangmi.plug.v3|米家智能插座增强版|512|
|chuangmi.plug.vtl_v1|小米智能插座（虚拟）|145|
|chuangmi.remote.732a02|小白蓝牙无线开关K2（单键版）|6973|
|chuangmi.remote.732b02|小白蓝牙无线开关K2（双键版）|6974|
|chuangmi.remote.h102a03|小白万能遥控器|65701|
|chuangmi.remote.h102c01|小白万能遥控器 声控版|1122|
|chuangmi.remote.v2|米家万能遥控器|65567|
|chuangmi.switch.725a02|小白智能墙壁开关K3（零火单键）|11312|
|chuangmi.switch.725b02|小白智能墙壁开关K3（零火双键）|11313|
|chuangmi.switch.725c02|小白智能墙壁开关K3（零火三键）|11314|
|chuangmi.switch.733a02|小白智能墙壁开关K2（零火单键）|6975|
|chuangmi.switch.733b02|小白智能墙壁开关K2（零火双键）|6976|
|chuangmi.switch.733c02|小白智能墙壁开关K2（零火三键）|6977|
|chuangmi.switch.mesh|小白智能开关零火版 K1-A|1350|
|chuangmi.switch.meshb01|小白智能开关零火版 K1-B|1490|
|chuangmi.switch.meshc01|小白智能开关零火版 K1-C|1489|
|citu.plug.dymcm3|电亿秒智能插排 CM3AM|37074|
|cjzz.switch.002|CJZZ 智能燃气报警开关|10432|
|cka001.switch.sw1a01|CKA一键复合开关|30847|
|cka001.switch.sw2a01|CKA二键复合开关|30848|
|cka001.switch.sw3a01|CKA三键复合开关|30849|
|cka001.switch.sw4a01|CKA四键复合开关|30850|
|ckcper.switch.bln001|Cpcker一键智能单火开关2.0|29462|
|ckcper.switch.bln002|Cpcker二键智能单火开关2.0|29463|
|ckcper.switch.bln003|Cpcker三键智能单火开关2.0|29464|
|ckcper.switch.sw1a01|Cpcker一键智能零火开关2.0|30155|
|ckcper.switch.sw2a01|Cpcker二键智能零火开关2.0|30156|
|ckcper.switch.sw3a01|Cpcker三键智能零火开关2.0|30157|
|ckcper.switch.sw4a01|Cpcker四键智能零火开关2.0|30158|
|cnph.plug.p30wxm|品禾安全定时插座(转换器)|21584|
|cqzx.switch.sw1a01|智信物联M1 Pro开关|19271|
|cqzx.switch.sw1a02|米驰M1 Pro开关|19600|
|cqzx.switch.sw3b01|智信物联四路屏显开关Mesh2.0|31234|
|creat6.switch.bln31|ANKOTTI安科帝智能一开（Mesh2.0）|22228|
|creat6.switch.bln32|ANKOTTI安科帝智能二开（Mesh2.0）|22229|
|creat6.switch.bln33|ANKOTTI安科帝智能三开（Mesh2.0）|22230|
|cuco.plug.co1|电小酷智能墙插CO1-M|72394|
|cuco.plug.co1d|电小酷智能墙插CO1-M|74788|
|cuco.plug.co3d|电小酷智能插座 CO3-M|8167|
|cuco.plug.cp1|电小酷智能插座 CP1|66556|
|cuco.plug.cp1c|电小酷智能插座 CP1-A|32268|
|cuco.plug.cp1d|电小酷智能插座CP1|74844|
|cuco.plug.cp1m|电小酷智能插座CP1-AM(计电量)|72056|
|cuco.plug.cp1md|电小酷智能插座CP1-AM(计电量)|74849|
|cuco.plug.cp2|电小酷智能插座CP2|67943|
|cuco.plug.cp2a|电小酷智能插座CP2-AM|72216|
|cuco.plug.cp2ac|电小酷智能插座CP2（BF版）|32602|
|cuco.plug.cp2ad|电小酷智能插座 CP2-AM|74787|
|cuco.plug.cp2d|电小酷智能插座 CP2|74772|
|cuco.plug.cp3a|电小酷智能插座CP3-AM|72217|
|cuco.plug.cp3ad|电小酷智能插座CP3-AM|74786|
|cuco.plug.cp5d|电小酷智能插座CP5|74793|
|cuco.plug.cp5prd|电小酷智能插座CP5 Pro|7948|
|cuco.plug.cp5pro|电小酷智能排插CP5 Pro|6587|
|cuco.plug.cp7pd|电小酷智能插座CP7Pro|10923|
|cuco.plug.p2|Gosund智慧扩充插座P2|75560|
|cuco.plug.p8amd|电小酷智能插座P8AM|75650|
|cuco.plug.sp5|电小酷智能排插CP5|69927|
|cuco.plug.wp12|Gosund 30W GaN智能排插WP12|12721|
|cuco.plug.wp5|Gosund智能插座WP5|66290|
|cuco.plug.wp5m|Gosund智能插座WP5-AM(计电量)|75662|
|cuco.switch.cs1|电小酷智能开关CS1（零火线单键版）|70465|
|cuco.switch.cs1d|电小酷智能开关CS1（零火线单键版）|74845|
|cuco.switch.cs2|电小酷智能开关CS2（零火线双键版）|70466|
|cuco.switch.cs2d|电小酷智能开关CS2（零火线双键版）|74846|
|cuco.switch.cs3|电小酷智能开关CS3（零火线三键版）|70428|
|cuco.switch.cs3d|电小酷智能开关CS3（零火线三键版）|74847|
|cuco.switch.s4amtd|电小酷智能开关S4AM(单火线单键版)|7917|
|cuco.switch.s4amts|电小酷智能开关S4AM （单火线单键版)|6511|
|cuco.switch.s5amtd|电小酷智能开关S5AM(单火线双键版)|7916|
|cuco.switch.s5amts|电小酷智能开关S5AM （单火线双键版)|6267|
|cuco.switch.s6amtd|电小酷智能开关S6AM(单火线三键版)|7915|
|cuco.switch.s6amts|电小酷智能开关S6AM （单火线三键版)|6266|
|cxw.plug.v1|Mesh智能插座系列V1|14737|
|cxw.remote.ble006|八情景调光调色智能旋钮|17825|
|cxw.remote.panv01|八键情景面板V1|19209|
|cxw.switch.swv01|Mesh智能通断器系列V1|16200|
|daolai.switch.k1|单路开关模块Mesh版|5692|
|daowei.switch.nolr01|道韦DS08屏显一键开关|34665|
|daowei.switch.nolr02|道韦DS08屏显二键开关|34666|
|daowei.switch.nolr03|道韦DS08屏显三键开关|34667|
|daowei.switch.sw1a01|道韦DS11系列零火智能开关一开|33869|
|daowei.switch.sw1b01|道韦DS01系列零火智能开关一开|33875|
|daowei.switch.sw1c01|道韦118DS单边键系列零火智能开关一开|33888|
|daowei.switch.sw1d01|道韦118DS任意键系列零火智能开关一开|33891|
|daowei.switch.sw1e01|道韦DS07系列零火智能开关一开|34361|
|daowei.switch.sw2a01|道韦DS11系列零火智能开关二开|33870|
|daowei.switch.sw2b01|道韦DS01系列零火智能开关二开|33876|
|daowei.switch.sw2c01|道韦118DS单边键系列零火智能开关二开|33889|
|daowei.switch.sw2d01|道韦118DS任意键系列零火智能开关二开|33892|
|daowei.switch.sw2e01|道韦DS07系列零火智能开关二开|34606|
|daowei.switch.sw3a01|道韦DS11系列零火智能开关三开|33871|
|daowei.switch.sw3a03|道韦DTS-60智能情景4寸屏开关|35039|
|daowei.switch.sw3b01|道韦DS01系列零火智能开关三开|33877|
|daowei.switch.sw3c01|道韦118DS单边键系列零火智能开关三开|33890|
|daowei.switch.sw3d01|道韦118DS任意键系列零火智能开关三开|33893|
|daowei.switch.sw3e01|道韦DS07系列零火智能开关三开|34607|
|daowei.switch.sw4a01|道韦DS11系列零火智能开关四开|33872|
|daowei.switch.sw4b01|道韦DS01系列零火智能开关四开|33878|
|daowei.switch.sw4e01|道韦DS07系列零火智能开关四开|36202|
|dba89.switch.alkg1|阿耀智能一键开关（Mesh2.0）|40582|
|dba89.switch.alkg2|阿耀智能二键开关（Mesh2.0）|40581|
|dba89.switch.alkg3|阿耀智能三键开关（Mesh2.0）|40580|
|dba89.switch.alkg4|阿耀智能四键开关（Mesh2.0）|40579|
|ddy.switch.sw4a02|SZGL智能感应开关四键Mesh版|15418|
|de1.plug.wjzncz|DEBROGLIE智能插座(Mesh2.0)|37056|
|de1.remote.wjwx8|DEBROGLIE无线八键开关（BLE）|35923|
|delai.switch.m61k|DELAI德徕智能开关(一开)|29750|
|delai.switch.m62k|DELAI德徕智能开关(二开)|29751|
|delai.switch.m63k|DELAI德徕智能开关(三开)|29752|
|delai.switch.m64k|DELAI德徕智能开关(四开)|29753|
|delai.switch.m66k|DELAI德徕智能开关(六开)|29754|
|delai.switch.m98k|DELAI德徕智能开关(八开)|29755|
|dfwlw.switch.xy02|希崖智能断路器|21862|
|dhzn.switch.sw0a01|乐智狗WIFI灯具通断器|2944|
|dlx.plug.deim01|德力西电气智能插座M01|31373|
|dlx.plug.deim02|德力西电气智能插座M02|31374|
|dlx.switch.1cd295|德力西电气CD295F智能墙壁开关(零火单键)|31531|
|dlx.switch.1d288|德力西电气DE288智能墙壁开关(单火单键)|35079|
|dlx.switch.1d295|德力西电气CD295F智能墙壁开关(单火单键)|35082|
|dlx.switch.1e288|德力西电气DE288智能墙壁开关（零火单键）|34962|
|dlx.switch.2cd295|德力西电气CD295F智能墙壁开关(零火双键)|31532|
|dlx.switch.2d288|德力西电气DE288智能墙壁开关(单火双键)|35080|
|dlx.switch.2d295|德力西电气CD295F智能墙壁开关(单火双键)|35083|
|dlx.switch.2e288|德力西电气DE288智能墙壁开关（零火双键）|34963|
|dlx.switch.3cd295|德力西电气CD295F智能墙壁开关(零火三键)|31533|
|dlx.switch.3d288|德力西电气DE288智能墙壁开关(单火三键)|35081|
|dlx.switch.3d295|德力西电气CD295F智能墙壁开关(单火三键)|35084|
|dlx.switch.3e288|德力西电气DE288智能墙壁开关（零火三键）|34964|
|dlx.switch.4cd295|德力西电气CD295F智能墙壁开关(零火四键)|31534|
|dlx.switch.4e288|德力西电气DE288智能墙壁开关（零火四键）|34965|
|dlx.switch.m01k|德力西电气一位零火智能开关|23537|
|dlx.switch.m02k|德力西电气二位零火智能开关|23538|
|dlx.switch.m03k|德力西电气三位零火智能开关|23539|
|dlx.switch.m04k|德力西电气四位零火智能开关|23540|
|dlx.switch.m11|德力西电气一位智能屏显免刻字复合面板|26267|
|dlx.switch.m12|德力西电气二位智能屏显免刻字复合面板|26270|
|dlx.switch.m13|德力西电气三位智能屏显免刻字复合面板|26271|
|dlx.switch.m14|德力西电气四位智能屏显免刻字复合面板|26272|
|dlx.switch.m14yp|德力西电气圆面屏智能中控面板|27082|
|dlx.switch.m14zk|德力西电气全屏智能多功能面板|27083|
|dlx.switch.md01k|德力西电气一位单零火智能开关|23541|
|dlx.switch.md02k|德力西电气二位单零火智能开关|23542|
|dlx.switch.md03k|德力西电气三位单零火智能开关|23543|
|dlx.switch.md04k|德力西电气四位单零火智能开关|23544|
|dnake.switch.bdlx1|狄耐克智能一键开关面板(单零火)|32472|
|dnake.switch.bdlx2|狄耐克智能二键开关面板(单零火)|32471|
|dnake.switch.bdlx3|狄耐克智能三键开关面板(单零火)|32470|
|dnake.switch.bln02|狄耐克智慧屏开关knob-Mesh版|21370|
|dnake.switch.bln04|狄耐克彩屏开关面板G2-Mesh版|20339|
|dnake.switch.bln10|狄耐克智慧屏开关Find-Mesh版|27081|
|dnake.switch.bln31|狄耐克智能一键开关面板（Mesh2.0）|27238|
|dnake.switch.bln32|狄耐克智能二键开关面板（Mesh2.0）|27239|
|dnake.switch.bln33|狄耐克智能三键开关面板（Mesh2.0）|27240|
|dnake.switch.bln34|狄耐克智能四键开关面板（Mesh2.0）|27241|
|dnake.switch.bln36|狄耐克智能六键开关面板（Mesh2.0）|27242|
|dnake.switch.blp01|狄耐克一键屏显开关面板(Mesh2.0)|30305|
|dnake.switch.blp02|狄耐克二键屏显开关面板(Mesh2.0)|30311|
|dnake.switch.blp03|狄耐克三键屏显开关面板(Mesh2.0)|30313|
|dnake.switch.blp04|狄耐克四键屏显开关面板(Mesh2.0)|30319|
|dnake.switch.blx1|狄耐克智能一键开关F46(Mesh2.0)|32469|
|dnake.switch.blx2|狄耐克智能二键开关F46(Mesh2.0)|32468|
|dnake.switch.blx3|狄耐克智能三键开关F46(Mesh2.0)|32467|
|dnake.switch.blx4|狄耐克智能四键开关F46(Mesh2.0)|32466|
|dnake.switch.pxu6|狄耐克智能四键屏显开关F46(Mesh2.0)|35661|
|dnake.switch.sw1b01|狄耐克智能一键开关面板|21114|
|dnake.switch.sw2b01|狄耐克智能二键开关面板|21115|
|dnake.switch.sw3b01|狄耐克智能三键开关面板|21116|
|dnake.switch.sw4b01|狄耐克智能四键开关面板|21117|
|dooya.remote.e1p|杜亚智能无线开关E1|23342|
|dooya.remote.e6|杜亚智能无线旋钮开关E6|21936|
|dooya.remote.ek1|向日葵智能面板EK1|23412|
|dooya.switch.sw1a01|杜亚智能开关灵智E5 单键|40146|
|dooya.switch.sw2a01|杜亚智能开关灵智E5 双键|40147|
|dooya.switch.sw3a01|杜亚智能开关灵智E5 三键|40148|
|dreame.switch.b011g|追觅智能开关（一开）|29700|
|dreame.switch.b012g|追觅智能开关（二开）|29701|
|dreame.switch.b013g|追觅智能开关（三开）|29702|
|dreame.switch.b031g|追觅智能开关Air（一开）|29707|
|dreame.switch.b032g|追觅智能开关Air（二开）|29708|
|dreame.switch.b033g|追觅智能开关Air（三开）|29710|
|dreame.switch.b041g|追觅智能开关Lite（一开）|30622|
|dreame.switch.b042g|追觅智能开关Lite（二开）|30623|
|dreame.switch.b043g|追觅智能开关Lite（三开）|30624|
|drui.switch.wtmk4|沃铁智能四键开关|34751|
|dwdz.switch.sw0a01|情景mesh通断器DBS版|4252|
|eda.switch.1sfsw|易而达MESH单火开关1键|5514|
|eda.switch.2sfsw|易而达MESH单火开关2键|5542|
|eda.switch.2sw|易而达MESH开关2键|4520|
|eda.switch.3sfsw|易而达MESH单火开关3键|5543|
|eda.switch.3sw|易而达MESH开关3键|4521|
|eda.switch.switch|易而达MESH开关1键|4519|
|emelit.switch.xmrp00|MixDALI智能开关面板|21188|
|emlng.switch.sw1a02|艾明丽智能通断器MESH2.0|40867|
|ezhome.switch.z4001|智汇云一位轻触开关面板|1888|
|ezhome.switch.z4002|智汇云二位轻触开关面板|1485|
|ezhome.switch.z4003|智汇云三位轻触开关面板|1484|
|fbt.switch.sw0a01|伟创智喆智能通断器|41225|
|feid.switch.fdw005|飞雕智薄一位零火智能开关|32068|
|feid.switch.fdw006|飞雕智薄二位零火智能开关|32069|
|feid.switch.fdw007|飞雕智薄三位零火智能开关|32070|
|feid.switch.fdw008|飞雕大板智能开关（零火四键）|32071|
|feid.switch.fdw009|飞雕智彩一位零火智能开关|36401|
|feid.switch.fdw010|飞雕智彩二位零火智能开关|36402|
|feid.switch.fdw011|飞雕智彩三位零火智能开关|36403|
|feid.switch.fdw012|飞雕智彩四位零火智能开关|36404|
|feid.switch.fdw013|飞雕智薄四位零火智能开关|36405|
|forick.remote.sw1b01|弗雷克智能无线旋钮遥控开关F6L|28907|
|forick.switch.flkkg4|弗雷克智能八键复合开关（Mesh2.0）|31146|
|forick.switch.sw1a01|弗雷克智能开关D6（单开）|28139|
|forick.switch.sw1b01|弗雷克智能开关D8（单开）|28143|
|forick.switch.sw2a01|弗雷克智能开关D6（双开）|28140|
|forick.switch.sw2b01|弗雷克智能开关D8（双开）|28144|
|forick.switch.sw3a01|弗雷克智能开关D6（三开）|28141|
|forick.switch.sw3b01|弗雷克智能开关D8（三开）|28146|
|forick.switch.sw4b01|弗雷克智能开关D8（四开）|28147|
|frfox.switch.bl01|一位开关-单火Mesh版|7855|
|frfox.switch.bl02|二位开关-单火Mesh版|7856|
|frfox.switch.bl03|三位开关-单火Mesh版|7857|
|ftd.switch.swttdq|FTD智能通断器Pro(MESH)|21341|
|fyw.switch.sw0a01|小微情景MESH通断器|4668|
|gamder.switch.3a03|家的科技 六位智能开关|28759|
|gamder.switch.jdkg1|家的智能 一位智能开关A|37752|
|gamder.switch.jdkg2|家的智能 二位智能开关 A|37753|
|gamder.switch.jdkg3|家的智能 三位智能开关 A|37754|
|gamder.switch.jdkg4|家的智能 四位智能开关 A|37755|
|gamder.switch.jdkg6|家的智能六位开关A|37756|
|gamder.switch.sw1a01|家的V93系列一位智能开关|27651|
|gamder.switch.sw1b01|家的科技 一位智能开关|28272|
|gamder.switch.sw2a01|家的V93系列二位智能开关|27652|
|gamder.switch.sw2b01|家的科技 二位智能开关|28273|
|gamder.switch.sw3a01|家的V93系列三位智能开关|27653|
|gamder.switch.sw3b01|家的科技 三位智能开关|28274|
|gamder.switch.sw4a01|家的V93系列四位带屏显智能开关|27654|
|gamder.switch.sw4b01|家的科技 四位智能开关|28275|
|gaosd.switch.gsp1k|高事达PLC智能一位复合开关(零火)|80979|
|gaosd.switch.gsp2k|高事达PLC智能二位复合开关(零火)|80118|
|gaosd.switch.gsp3k|高事达PLC智能三位复合开关(零火)|80978|
|gaosd.switch.gsp4k|高事达PLC智能四位复合开关(零火)|80020|
|gaosd.switch.gsp6k|高事达PLC智能六位复合开关(零火)|80019|
|gaosd.switch.gsp8k|高事达PLC智能八位复合开关(零火)|79876|
|gayoo.switch.gykgg1|光言光语 一键智能开关Mesh2.0|29821|
|gayoo.switch.gykgg2|光言光语 二键智能开关Mesh2.0|29822|
|gayoo.switch.gykgg3|光言光语 三键智能开关Mesh2.0|29823|
|gayoo.switch.gykgg4|光言光语 四键智能开关Mesh2.0|29824|
|ghzm.switch.ghkg1|冠华晓系列一键开关|39545|
|ghzm.switch.ghkg2|冠华晓系列二键开关|39546|
|ghzm.switch.ghkg3|冠华晓系列三键开关|39547|
|ghzm.switch.ghkg4|冠华晓系列四键开关|39544|
|giot.plug.v3shsm|V3智能单插（Mesh）|10920|
|giot.plug.v6shsm|V6智能单插（Mesh）|16415|
|giot.plug.v7icm|Gra智能控制器V7（Mesh）|23928|
|giot.plug.v7icw|Gra智能控制器V7（WiFi）|23929|
|giot.plug.v8icm|Gra电计量控制器V8（Mesh）|21478|
|giot.plug.v9icm|Gra智能控制器V7（Mesh2.0）|22741|
|giot.plug.v9icwf|Gra电计量控制器V8（WiFi）|19399|
|giot.remote.v51kwm|V5无线一键开关 （BLE）|16191|
|giot.remote.v52kwm|V5无线二键开关 （BLE）|16180|
|giot.remote.v53kwm|V5无线三键开关 （BLE）|16181|
|giot.remote.v54kwm|V5无线四键开关 （BLE）|16182|
|giot.remote.v56kwm|V5无线六键开关（BLE）|16184|
|giot.remote.v58kwm|V5无线八键开关 （BLE）|16186|
|giot.switch.v3oodm|V3智能通断器（Mesh）|10944|
|giot.switch.v51ksm|V5智能一键开关（Mesh）|13138|
|giot.switch.v52ksm|V5智能二键开关（Mesh）|13139|
|giot.switch.v53ksm|V5智能三键开关（Mesh）|13140|
|giot.switch.v54ksm|V5智能四键开关（Mesh）|13141|
|giot.switch.v61ksm|V6智能一路开关（Mesh）|16401|
|giot.switch.v62ksm|V6智能二路开关（Mesh）|16400|
|giot.switch.v63ksm|V6智能三路开关（Mesh）|16366|
|giot.switch.v64ksm|V6智能四路开关（Mesh）|16359|
|giot.switch.v6oodm|V6智能通断器（Mesh）|15461|
|giot.switch.v81ksm|V8Gra智能一路开关（Mesh2.0）|20446|
|giot.switch.v82ksm|V8Gra智能二路开关（Mesh2.0）|20447|
|giot.switch.v83ksm|V8Gra智能三路开关（Mesh2.0）|20448|
|giot.switch.v84ksm|V8Gra智能四路开关（Mesh2.0）|20449|
|giwu.switch.f01|GW一位开关Q1+1|31212|
|giwu.switch.f02|GW二位开关Q2+2|31211|
|giwu.switch.f03|GW三位开关Q3+3|31210|
|giwu.switch.g01|GW一位开关G1|31208|
|giwu.switch.g02|GW二位开关G2|31207|
|giwu.switch.g03|GW三位开关G3|31206|
|giwu.switch.g04|GW四位开关G4|31205|
|giwu.switch.gw01|即屋一位智能开关|24612|
|giwu.switch.gw02|即屋二位智能开关|24611|
|giwu.switch.gw03|即屋三位智能开关|24610|
|giwu.switch.gw04|即屋四位智能开关|24526|
|giwu.switch.gwqj04|即屋八位场景开关|24614|
|giwu.switch.sw1a01|GW灵动岛一位屏显开关U1|33082|
|giwu.switch.sw2a01|GW灵动岛二位屏显开关U2|33083|
|giwu.switch.sw3a01|GW灵动岛三位屏显开关U3|33084|
|giwu.switch.sw3a03|即屋场景开关屏T3|32179|
|giwu.switch.sw4a01|GW灵动岛四位屏显开关U4|33085|
|googo.remote.gnxn4|mitch无线旋钮开关|38866|
|googo.switch.sw1a01|mitch一开屏显开关青春版(Mesh2.0)|27329|
|googo.switch.sw1a02|mitch一路智能开关Mesh2.0|29171|
|googo.switch.sw2a01|mitch二开屏显开关青春版(Mesh2.0)|27330|
|googo.switch.sw2a02|mitch二路智能开关Mesh2.0|29172|
|googo.switch.sw3a01|mitch三开屏显开关青春版(Mesh2.0)|27331|
|googo.switch.sw3a02|mitch三路智能开关Mesh2.0|29173|
|googo.switch.sw4a01|mitch四路屏显智能开关Mesh2.0|27332|
|googo.switch.sw4a02|mitch四路智能开关Mesh2.0|29174|
|googo.switch.sw4a03|mitch四开屏显开关青春版(Mesh2.0)|32229|
|googo.switch.sw4a04|mitch玄鸟四路屏显开关(Mesh2.0)|36019|
|googo.switch.sw4b02|mitch四键屏显开关PRO版(Mesh2.0)|32512|
|googo.switch.sw8a01|mitch八路智能开关Mesh2.0|27333|
|gosvn.switch.sw0a01|Gosvn高山领航智能阀门控制器WiFi版|5894|
|gosvn.switch.sw1a01|Gosvn高山领航一位智慧开关WiFi版|5899|
|gosvn.switch.sw2a01|Gosvn高山领航二位智慧开关WiFi版|5900|
|gosvn.switch.sw3a01|Gosvn高山领航三位智慧开关WiFi版|5901|
|graiot.switch.bln001|Graun智能一键开关|29218|
|graiot.switch.bln002|Graun智能二键开关|29219|
|graiot.switch.bln003|Graun智能三键开关|29220|
|graiot.switch.bln004|Graun智能四键开关|29221|
|graiot.switch.bln006|Graun智能六键开关|29222|
|graiot.switch.bln008|Graun智能八键开关|29223|
|gran.switch.four|无线物联零火四键开关|5402|
|gran.switch.one|无线物联零火单键开关|5097|
|gran.switch.three|无线物联零火三键开关|5105|
|gran.switch.two1|无线物联零火双键开关|5103|
|gsd.switch.sw1a01|GSD一键智能开关|9910|
|gsd.switch.sw2a01|GSD二键智能开关|9911|
|gsd.switch.sw3a01|GSD三键智能开关|9912|
|gsd.switch.sw4a01|GSD四键智能开关|9913|
|gsd.switch.sw8a01|GSD八键智能开关|9961|
|gt1688.switch.sw1a01|自然爱开关SW6 Mesh2.0 一键|25629|
|gt1688.switch.sw2a01|自然爱开关SW6 Mesh2.0 二键|25630|
|gt1688.switch.sw3a01|自然爱开关SW6 Mesh2.0 三键|25631|
|gt1688.switch.sw4a01|自然爱开关SW6 Mesh2.0 四键|25632|
|gtop.switch.yd01|智悦智能开关|8468|
|gudi.switch.gdp002|固帝智能屏显开关零火二开|31886|
|gudi.switch.gdp005|固帝智能屏显开关零火一开|31986|
|gudi.switch.gdp006|固帝智能屏显开关零火三开|31987|
|gudi.switch.gdp007|固帝智能屏显开关零火四开|31988|
|gudi.switch.gdy002|固帝超薄圆屏多功能面板|31989|
|gudi.switch.sw1a01|固帝 A9智能开关1键|29269|
|gudi.switch.sw2a01|固帝 A9智能开关2键|29270|
|gudi.switch.sw3a01|固帝 A9智能开关3键|29271|
|gudi.switch.sw3d01|固帝 智能开关四寸屏|32005|
|gudi.switch.sw4a01|固帝 A9智能开关屏显4键|29272|
|gudi.switch.sw4b01|固帝 A9智能开关4键|32759|
|gudi.switch.swy001|固帝A96彩屏智能开关二键|36596|
|gudi.switch.swy002|固帝A96彩屏智能开关三键|36597|
|gudi.switch.swy003|固帝A96彩屏智能开关四键|36598|
|gudi.switch.swy004|固帝D06智能开关一键|37686|
|gudi.switch.swy005|固帝D06智能开关二键|37687|
|gudi.switch.swy006|固帝D06智能开关三键|37688|
|gudi.switch.swy007|固帝D06智能开关四键|37689|
|gudi.switch.swy008|固帝A96彩屏智能开关一键|39497|
|guixin.switch.sw0a01|U-FAMILY Mesh通断器09|34324|
|guixin.switch.sw0a02|U-FAMILY WiFi通断器V9|34360|
|guznos.remote.gzxn4|光正中枢无线旋钮开关|38865|
|guznos.switch.gzkg1|GZ 一位智能开关|30000|
|guznos.switch.gzkg2|GZ 二位智能开关|30002|
|guznos.switch.gzkg3|GZ 三位智能开关|30004|
|guznos.switch.gzkg4|GZ 四位智能开关|30005|
|gxhl.switch.7zds11|7z一路智能调光开关|72596|
|gxhl.switch.7zds12|7z二路智能调光开关|72539|
|gxhl.switch.7zsw11|7z一键智能开关|71291|
|gxhl.switch.7zsw12|7z二键智能开关|71292|
|gxhl.switch.7zsw13|7z三键智能开关|71298|
|gzjp.switch.sw4a01|JP四键开关|26666|
|gzzn.switch.sw1a01|antjiujiu智能开关 蚁柔pro一位|29378|
|gzzn.switch.sw2a01|antjiujiu智能开关 蚁柔pro二位|29379|
|gzzn.switch.sw3a01|antjiujiu智能开关 蚁柔pro三位|29380|
|gzzn.switch.sw4a01|antjiujiu智能开关 蚁柔pro四位|29383|
|h2t528.plug.outlet|浩翔联智蓝牙Mesh计量插座|24000|
|hanyu1.switch.sw1a01|汉语H8田字格智能开关（一开）|36566|
|hanyu1.switch.sw1b01|汉语H3智能开关（一开）|36570|
|hanyu1.switch.sw2a01|汉语H8田字格智能开关（二开）|36567|
|hanyu1.switch.sw2b01|汉语H3智能开关（二开）|36571|
|hanyu1.switch.sw3a01|汉语H8田字格智能开关（三开）|36568|
|hanyu1.switch.sw3b01|汉语H3智能开关（三开）|36572|
|hanyu1.switch.sw4a01|汉语H8田字格智能开关（四开）|36569|
|hanyu1.switch.sw4b01|汉语H3智能开关（四开）|36573|
|haoyi.remote.hyxn4|皓逸智能无线旋钮开关（中枢版）|39769|
|haoyi.switch.hyv1s4|皓逸四键智能开关V1|30502|
|haoyi.switch.sw0a01|皓逸单路通断器（Max）|20667|
|haoyi.switch.sw0a02|皓逸智能双路通断器|38799|
|haoyi.switch.sw1a01|皓逸智能开关一开Q7Pro（屏显版）|23677|
|haoyi.switch.sw2a01|皓逸智能开关二开Q7Pro（屏显版）|23678|
|haoyi.switch.sw3a01|皓逸智能开关三开Q7Pro（屏显版）|23679|
|haoyi.switch.sw4a01|皓逸智能开关四开Q7pro（屏显版）|23680|
|hbg.remote.hzwx1|汉烛一键无线开关|39570|
|hbg.remote.hzwx2|汉烛二键无线开关|39571|
|hbg.remote.hzwx3|汉烛三键无线开关|39572|
|hbg.remote.hzwx4|汉烛四键无线开关|39573|
|hbg.remote.hzwx8|汉烛八键无线开关|39569|
|hbg.switch.hzkgv1|汉烛一键智能开关|39741|
|hbg.switch.hzkgv2|汉烛二键智能开关|39742|
|hbg.switch.hzkgv3|汉烛三键智能开关|39743|
|hbg.switch.hzkgv4|汉烛四键智能开关|39744|
|hbg.switch.hztdq|汉烛智能通断器（Mesh2.0）|39739|
|hbg.switch.hztdq2|汉烛智能通断器（WIFI）|39740|
|hey.plug.n100|微断云控智能断路器N1|19976|
|hey.relay.h100|微断云控智能控制器|9784|
|hey.switch.x100|微断云控|5541|
|hgkj.switch.kg1|鸿光科技一键智能开关Mesh2.0|31661|
|hgkj.switch.kg2|鸿光科技二键智能开关Mesh2.0|31662|
|hgkj.switch.kg3|鸿光科技三键智能开关Mesh2.0|31664|
|hgkj.switch.kg4|鸿光科技四键智能开关Mesh2.0|31665|
|hgzm.switch.v81ksm|河光智能一键开关（Mesh2.0）|28223|
|hipc.plug.m1|HiPC电脑智能开机卡|21292|
|hnlc.switch.sw1a01|7z智能灯控开关-1路|29479|
|hnlc.switch.sw2a01|7z智能灯控开关-2路|29478|
|hnlc.switch.sw3a01|7z智能灯控开关-3路|28239|
|honkon.switch.hgkgv1|宏光灵悦一键开关|36578|
|honkon.switch.hgkgv2|宏光灵悦二键开关|36577|
|honkon.switch.hgkgv3|宏光灵悦三键开关|36576|
|honkon.switch.hgkgv4|宏光灵悦四键开关|36575|
|honyar.plug.cz01|鸿雁智能插座IHC8406M|24627|
|honyar.plug.hyrccz|鸿雁毫米波节能转换插座|29643|
|honyar.plug.plug2|鸿雁GM系列智能轨道插座|32737|
|honyar.plug.v7icm|鸿雁智能插座|27833|
|honyar.switch.bln01|HONYAR一键智能开关|31866|
|honyar.switch.bln02|HONYAR二键智能开关|31867|
|honyar.switch.bln03|HONYAR三键智能开关|31868|
|honyar.switch.bln04|HONYAR四键智能开关|31869|
|honyar.switch.dl001|鸿雁三键轻触开关W3-86K31ND5-BD-M-PRO|26918|
|honyar.switch.dl002|鸿雁双键轻触开关W3-86K21ND5-BD-M-PRO|26924|
|honyar.switch.dl003|鸿雁单键轻触开关W3-86K11ND5-BD-M-PRO|26925|
|honyar.switch.hyp007|鸿雁单键智能开关Pro|34994|
|honyar.switch.hyp008|鸿雁双键智能开关Pro|34995|
|honyar.switch.hyp009|鸿雁三键智能开关Pro|34996|
|honyar.switch.hyp010|鸿雁四键智能开关Pro|34997|
|honyar.switch.k11bd|鸿雁单键开关K11ND10-BD|20682|
|honyar.switch.k21bd|鸿雁双键开关K21ND10-BD|20684|
|honyar.switch.k31bd|鸿雁三键开关K31ND10-BD|20685|
|honyar.switch.px|鸿雁全面屏开关HM1Plus|30373|
|honyar.switch.sw1a01|鸿雁单键智能开关|23773|
|honyar.switch.sw1b01|鸿雁单键智能触摸开关|24674|
|honyar.switch.sw1c01|鸿雁超薄单键智能开关|26296|
|honyar.switch.sw1c04|鸿雁单键智能开关|34146|
|honyar.switch.sw1d01|鸿雁单键智能开关HM1 pro|27803|
|honyar.switch.sw1e01|鸿雁单键智能按键开关|32550|
|honyar.switch.sw2a01|鸿雁双键智能开关|23774|
|honyar.switch.sw2b01|鸿雁双键智能触摸开关|24675|
|honyar.switch.sw2c01|鸿雁超薄双键智能开关|26297|
|honyar.switch.sw2c04|鸿雁双键智能开关|34147|
|honyar.switch.sw2d01|鸿雁双键智能开关HM1 pro|27804|
|honyar.switch.sw2e01|鸿雁双键智能按键开关|32551|
|honyar.switch.sw3a|鸿雁空气监测开关|32417|
|honyar.switch.sw3a01|鸿雁三键智能开关|23775|
|honyar.switch.sw3b01|鸿雁三键智能触摸开关|24676|
|honyar.switch.sw3c01|鸿雁超薄三键智能开关|26298|
|honyar.switch.sw3c04|鸿雁三键智能开关|34148|
|honyar.switch.sw3d01|鸿雁三键智能开关HM1 pro|27805|
|honyar.switch.sw3e01|鸿雁三键智能按键开关|32552|
|honyar.switch.sw4a01|鸿雁四键智能开关|23776|
|honyar.switch.sw4b01|鸿雁四键智能触摸开关|24677|
|honyar.switch.sw4c04|鸿雁四键智能开关|34149|
|honyar.switch.sw4d01|鸿雁四键智能开关HM1 pro|27806|
|honyar.switch.sw4e01|鸿雁四键智能按键开关|32553|
|hope.switch.g7|智慧屏开关M4|15957|
|hope.switch.w1|智慧屏开关|73972|
|hope.switch.x3|X3智慧开关|10620|
|hszn.switch.hskg1|华时智能一路开关（Mesh2.0）|31148|
|hszn.switch.hskg2|华时智能二路开关（Mesh2.0）|31149|
|hszn.switch.hskg3|华时智能三路开关（Mesh2.0）|31150|
|hszn.switch.hskg4|华时智能四路开关（Mesh2.0）|31151|
|hszna.switch.h0001|辉帅一位零火智能开关|32121|
|hszna.switch.h0002|辉帅二位零火智能开关|32122|
|hszna.switch.h0003|辉帅三位零火智能开关|32123|
|hszna.switch.h0004|辉帅四位零火智能开关|32124|
|hszna.switch.h0005|辉帅全面屏智能面板|32125|
|hszna.switch.h0006|辉帅圆屏多功能面板|32126|
|huafu.switch.sw1a01|HF情景智能一键开关|33913|
|huafu.switch.sw2a01|HF情景智能二键开关|33914|
|huafu.switch.sw3a01|HF情景智能三键开关|33915|
|huafu.switch.sw4a01|HF情景智能四键开关|33916|
|huayi.switch.v0001|慧作智能开关(零火线单键版)|1915|
|huayi.switch.v0002|慧作智能开关(零火线双键版)|1914|
|huca.plug.cz2|H+智能插座（WiFi版）|26581|
|huca.plug.cz2b|H+智能插座（蓝牙Mesh版）|26580|
|huca.remote.wx8|H+无线场景八键开关|12382|
|huca.switch.2lh1|H+ 轻触智能开关单键|19472|
|huca.switch.2lh2|H+ 轻触智能开关双键|19471|
|huca.switch.2lh3|H+ 轻触智能开关三键|19130|
|huca.switch.dh1|H+单火开关|8614|
|huca.switch.dh2|H+单火双键开关|8613|
|huca.switch.dh3|H+单火三键开关|6850|
|huca.switch.dhs1|H+智能开关单键（单火/零火通用版）|21305|
|huca.switch.dhs2|H+智能开关双键（单火/零火通用版）|21523|
|huca.switch.dhs3|H+智能开关三键（单火/零火通用版）|21524|
|huca.switch.dhs4|H+智能开关四开（零火版）|28656|
|huca.switch.h2mb01|H+ 微动智能开关 单键|19879|
|huca.switch.h2mb02|H+ 微动智能开关 双键|19880|
|huca.switch.h2mb03|H+ 微动智能开关 三键|19881|
|huca.switch.hc3m11|H+超薄智能开关 单键|19907|
|huca.switch.hc3m21|H＋超薄智能开关 双键|19908|
|huca.switch.hc3m31|H+ 超薄智能开关 三键|19909|
|huca.switch.lh1|H+零火单键开关|15109|
|huca.switch.lh2|H+零火双键开关|15110|
|huca.switch.lh3|H+零火三键开关|15111|
|huca.switch.lh4|H+零火四键开关|11893|
|hyzngc.cs.zmqd|蓝牙Mesh插卡取电|11548|
|hyzngc.switch.hy0601|智能一键开关（零火mesh）|5924|
|hyzngc.switch.hy0602|智能二键开关（零火mesh）|6277|
|hyzngc.switch.hy0603|智能三键开关（零火mesh）|6332|
|hyzngc.switch.zm0601|一键智能开关（零火mesh）|11544|
|hyzngc.switch.zm0602|二键智能开关（零火mesh）|11545|
|hyzngc.switch.zm0603|三键智能开关（零火mesh）|11546|
|hyzngc.switch.zm0604|四键智能开关（零火mesh）|11547|
|hyznzm.switch.sw1a01|华艺一键智能开关|31323|
|hyznzm.switch.sw2a01|华艺二键智能开关|31325|
|hyznzm.switch.sw3a01|华艺三键智能开关|31327|
|hyznzm.switch.sw4a01|华艺四键智能开关|31328|
|hyznzm.switch.sw4b01|华艺屏显四键智能开关|31424|
|hzyk.plug.c4|初刻良品智能排插(WiFi)|27622|
|innolinks.plug.ap3200|空调智能插座|198|
|intac.remote.air04|视科四键旋钮无线开关R1|31626|
|iot.plug.cm2|电亿秒CM2计量插座|21113|
|iot.plug.jdls1|智能计电量插座M1|16170|
|iot.plug.pw6u1|岚威六路智能计量分控排插|16970|
|iot.plug.socn1|智能插座P1|13108|
|iot.switch.bjtdq5|QD智能通断器WiFi版|19437|
|iot.switch.jdltdq|计电量Mesh智能控制器|19142|
|iot.switch.kg21m|浦安达零火智能开关（一开）|17321|
|iot.switch.kg22m|浦安达零火智能开关（二开）|17322|
|iot.switch.kg23m|浦安达零火智能开关（三开）|17326|
|iot.switch.padw2p|浦安达单相智能保护开关|16291|
|iot.switch.padwb1|浦安达三相智能保护开关|11885|
|iot.switch.tdq3|QD智能通断器Mesh版|17725|
|isa.switch.kg01hl|小米米家屏显开关（单开单控）|2715|
|isa.switch.kg02hl|小米米家屏显开关（双开单控）|2716|
|isa.switch.kg03hl|小米米家屏显开关（三开单控）|2717|
|isur.switch.sw1b01|ISURPASS智能一路通断器|39689|
|isur.switch.sw2b01|ISURPASS智能二路通断器|39690|
|ivtec.plug.v5|Iwytech智能插座V5|13636|
|iwn.plug.iws007|IWN小铃铛智能计量插座|35900|
|iwn.switch.iws003|IWN小铃铛彩屏按键一位零火智能开关|35896|
|iwn.switch.iws004|IWN小铃铛彩屏按键二位零火智能开关|35897|
|iwn.switch.iws005|IWN小铃铛彩屏按键三位零火智能开关|35898|
|iwn.switch.iws006|IWN小铃铛彩屏按键四位零火智能开关|35899|
|iwn.switch.iws008|IWN小铃铛全面屏智能面板开关|40072|
|jbl123.switch.sw1a01|金百丽1位智能开关|23845|
|jbl123.switch.sw2a01|金百丽2位智能开关|23846|
|jbl123.switch.sw3a01|金百丽3位智能开关|23847|
|jbl123.switch.sw4a01|金百丽4位智能开关|23848|
|jdjz.switch.jzl1|京东京造智能墙壁开关（MESH2.0 单火单键）|32826|
|jdjz.switch.jzl2|京东京造智能墙壁开关（MESH2.0 单火双键）|32825|
|jdjz.switch.jzl3|京东京造智能墙壁开关（MESH2.0 单火三键）|32819|
|jdjz.switch.jzn1|京东京造智能墙壁开关（MESH2.0 零火单键）|30163|
|jdjz.switch.jzn2|京东京造智能墙壁开关（MESH2.0 零火双键）|30162|
|jdjz.switch.jzn3|京东京造智能墙壁开关（MESH2.0 零火三键）|30102|
|jgb.switch.jbgtdq|积歌必情景通断器（Mesh）|40651|
|jmzc.switch.zcs01|哲成智能一位零火智能开关|30206|
|jmzc.switch.zcs02|哲成智能二位零火智能开关|30205|
|jmzc.switch.zcs03|哲成智能三位零火智能开关|30204|
|jmzc.switch.zcs04|哲成智能四位零火智能开关|30203|
|jmzc.switch.zcs05|哲成智能圆屏多功能面板|30202|
|jmzc.switch.zcy01|哲成智能M18屏键一位零火智能开关Max|37690|
|jmzc.switch.zcy02|哲成智能M18屏键二位零火智能开关Max|37691|
|jmzc.switch.zcy03|哲成智能M18屏键三位零火智能开关Max|37692|
|jmzc.switch.zcy04|哲成智能M18屏键四位零火智能开关Max|37693|
|jtjiot.switch.sw1a01|捷特佳智能零火开关M1|38626|
|jtjiot.switch.sw2a01|捷特佳智能零火开关M2|38627|
|jtjiot.switch.sw3a01|捷特佳智能零火开关M3|38628|
|jtjiot.switch.sw4a04|捷特佳智能彩屏开关M8|38584|
|julun.remote.jlxn4|julun中枢旋钮开关|40114|
|julun.switch.jlsw01|julun智能WIFI开关|69990|
|junon.switch.jlkg1|俊朗智能一路开关（Mesh2.0）|29846|
|junon.switch.jlkg2|俊朗智能二路开关（Mesh2.0）|29847|
|junon.switch.jlkg3|俊朗智能三路开关（Mesh2.0）|29848|
|jyds.plug.pc01|PNTU国际电工智能轨道插座|32339|
|jyds.switch.pt01|PNTU国际电工一键智能开关|31578|
|jyds.switch.pt02|PNTU国际电工二键智能开关|31579|
|jyds.switch.pt03|PNTU国际电工三键智能开关|31580|
|jyds.switch.pt04|PNTU国际电工四键智能开关|31581|
|jyds.switch.px01|PNTU国际电工一键屏显开关|31582|
|jyds.switch.px02|PNTU国际电工二键屏显开关|31583|
|jyds.switch.px03|PNTU国际电工三键屏显开关|31584|
|jyzc.switch.jykg4|捷易智能四路开关（Mesh2.0）|31233|
|kalami.switch.bln31|Aioaie智能一键屏显开关|28899|
|kalami.switch.bln32|Aioaie智能二键屏显开关|28900|
|kalami.switch.bln33|Aioaie智能三键屏显开关|28901|
|kalami.switch.klmk1|Aioaie一键智能开关|29437|
|kalami.switch.klmk2|Aioaie二键智能开关|29438|
|kalami.switch.klmk3|Aioaie三键智能开关|29439|
|kalami.switch.klmk4|Aioaie四键智能开关|29440|
|kalami.switch.m4px01|Aioaie智能一键屏显开关M4|36492|
|kalami.switch.m4px02|Aioaie智能二键屏显开关M4|36493|
|kalami.switch.m4px03|Aioaie智能三键屏显开关M4|36494|
|kalami.switch.m4sw01|Aioaie一键智能开关M4|36751|
|kalami.switch.m4sw02|Aioaie二键智能开关M4|36752|
|kalami.switch.m4sw03|Aioaie三键智能开关M4|36753|
|kalami.switch.m5px01|Aioaie智能一键屏显开关M5|36495|
|kalami.switch.m5px02|Aioaie智能二键屏显开关M5|36496|
|kalami.switch.m5px03|Aioaie智能三键屏显开关M5|36497|
|kalami.switch.ptm501|Aioaie一键智能开关M5|36754|
|kalami.switch.ptm502|Aioaie二键智能开关M5|36755|
|kalami.switch.ptm503|Aioaie三键智能开关M5|36756|
|kalami.switch.sw3a03|Aioaie4寸场景屏开关|35755|
|kanway.switch.sw4a01|Kanway 轻触开关零火D-4K|14417|
|katai.switch.sw1b01|katai一键智能开关Ultra|40871|
|katai.switch.sw2b01|katai二键智能开关Ultra|40872|
|katai.switch.sw3b01|katai三键智能开关Ultra|40873|
|katai.switch.sw4b01|katai四键智能开关Ultra|40874|
|keey.remote.qywx4|KEEY智能无线开关M|31813|
|keey.switch.qyfkg2|KEEY 云镜二键智能复合开关|35794|
|keey.switch.qyfkg3|KEEY 云镜三键智能复合开关|35795|
|keey.switch.qyfkg4|KEEY 云镜四键智能复合开关|35796|
|keey.switch.qykgm1|KEEY智能一键开关（Mesh2.0）|29634|
|keey.switch.qykgm2|KEEY智能二键开关（Mesh2.0）|29635|
|keey.switch.qykgm3|KEEY智能三键开关（Mesh2.0）|29636|
|keey.switch.qykgm4|KEEY智能四键开关（Mesh2.0）|29637|
|keey.switch.qytkg1|KEEY 智能一键复合开关 M2pro|37772|
|keey.switch.qytkg2|KEEY 智能二键复合开关 M2pro|37773|
|keey.switch.qytkg3|KEEY 智能三键复合开关 M2pro|37774|
|keey.switch.qytkg4|KEEY 智能四键复合开关 M2pro|37775|
|kegu.switch.kgkg1|KGP智能屏显一位开关|33334|
|kegu.switch.kgkg2|KGP智能屏显二位开关|32887|
|kegu.switch.kgkg3|KGP智能屏显三位开关|32886|
|kegu.switch.sw2a01|KGP智能二位开关（Mesh2.0）|30652|
|kegu.switch.sw3a01|KGP智能三位开关（Mesh2.0）|30651|
|kegu.switch.sw4a01|KGP智能四位开关（Mesh2.0）|30650|
|kemiqi.switch.kmw01|科米其智能开关（零火一键）|22523|
|kemiqi.switch.kmw02|科米其智能开关（零火二键）|22524|
|kemiqi.switch.kmw03|科米其智能开关（零火三键）|22525|
|kemiqi.switch.kmw04|科米其智能开关（零火四键）|22526|
|kemiqi.switch.kmw11|科米其智能多功能面板Mesh2.0|27414|
|kemiqi.switch.kmw12|科米其智能开关（零火一键）Mesh2.0|27531|
|kemiqi.switch.kmw13|科米其智能开关（零火二键）Mesh2.0|27532|
|kemiqi.switch.kmw14|科米其智能开关（零火三键）Mesh2.0|27533|
|kemiqi.switch.kmw15|科米其智能开关（零火四键）Mesh2.0|27534|
|kk2022.switch.bln31|KX单键灯控面板|24130|
|kk2022.switch.bln32|KX双键灯控面板|24136|
|kk2022.switch.bln33|KX三键灯控面板|24137|
|kk2022.switch.bln34|KX四键灯控面板|24138|
|kk2022.switch.bln38|KX八键复合开关面板|29516|
|kk2022.switch.bln41|KX单键灯控开关面板(单零火)|29037|
|kk2022.switch.bln42|KX双键灯控开关面板(单零火)|29038|
|kk2022.switch.bln43|KX三键灯控开关面板(单零火)|29039|
|kk2022.switch.blp01|KX屏显单键开关面板|26605|
|kk2022.switch.blp02|KX屏显双键开关面板|26606|
|kk2022.switch.blp03|KX屏显三键开关面板|26607|
|kk2022.switch.blp04|KX屏显四键开关面板|26608|
|kk2022.switch.sw1a01|单键灯控面板零火mesh版|11878|
|kk2022.switch.sw2a01|双键灯控面板零火mesh版|11879|
|kk2022.switch.sw3a01|三键灯控面板零火mesh版|11880|
|kk2022.switch.sw4a01|四键灯控面板零火mesh版|11881|
|kk2022.switch.sw8a01|RX八键复合面板零火mesh版|14102|
|klf888.switch.8a01|客来福智能开关八键|20636|
|klf888.switch.sw1a01|客来福智能开关A系列一开|20741|
|klf888.switch.sw1b01|客来福智能开关B系列一开|20767|
|klf888.switch.sw2a01|客来福智能开关A系列二开|20743|
|klf888.switch.sw2b01|客来福智能开关B系列二开|20768|
|klf888.switch.sw3a01|客来福智能开关A系列三开|20744|
|klf888.switch.sw3b01|客来福智能开关B系列三开|20769|
|klf888.switch.sw3c01|客来福智能家庭面板M4|20835|
|klf888.switch.sw4a01|客来福智能开关A系列四开|20746|
|klf888.switch.sw4b01|客来福智能开关B系列四开|20770|
|kmt.switch.m4px01|KOMACHT智慧Ai超薄一键屏显开关|36380|
|kmt.switch.m4px02|KOMACHT智慧Ai超薄二键屏显开关|36381|
|kmt.switch.m4px03|KOMACHT智慧Ai超薄三键屏显开关|36382|
|koey.switch.sw1a01|KOEY瞬系列智能开关1键|19062|
|koey.switch.sw1b01|KOEY瞬系列超薄智能开关1键|27371|
|koey.switch.sw2a01|KOEY瞬系列智能开关2键|19063|
|koey.switch.sw2b01|KOEY瞬系列超薄智能开关2键|27372|
|koey.switch.sw3a01|KOEY瞬系列智能开关3键|19064|
|koey.switch.sw3b01|KOEY瞬系列超薄智能开关3键|27373|
|koey.switch.sw4a01|KOEY瞬系列智能开关4键|19067|
|koey.switch.sw4b01|KOEY瞬系列超薄智能开关4键（屏显）|27374|
|ksc.switch.px1k1|金云智联墙壁开关X1（单键 PLC版）|80926|
|ksc.switch.px1k4|金云智联墙壁开关X1（四键 PLC版）|80930|
|ksks.switch.sw2a01|今上智能开关S3 双键|29021|
|ksks.switch.sw3a01|今上智能开关S2|18732|
|ksks.switch.sw3a02|今上智能开关S2 三键|34273|
|ksks.switch.sw3a03|今上智能开关S3 三键|27813|
|ksks.switch.sw4a01|今上智能开关S1|22899|
|ksks.switch.sw4a02|今上智能开关S1 四键|33881|
|ksks.switch.sw4a03|今上智能开关S1 Pro 四键屏显版|33882|
|ksmart.switch.sw1a01|控客轻智家轻宸超薄开关单键mesh2.0|30393|
|ksmart.switch.sw1b01|KONKE单路智控开关|30864|
|ksmart.switch.sw2a01|控客轻智家轻宸超薄开关双键mesh2.0|30394|
|ksmart.switch.sw2b01|KONKE双路智控开关|30865|
|ksmart.switch.sw3a01|控客轻智家轻宸超薄开关三键mesh2.0|30395|
|ksmart.switch.sw3b01|KONKE三路智控开关|30866|
|ksmart.switch.sw4a01|控客轻智家轻宸超薄开关四键mesh2.0|30396|
|ksmart.switch.sw4a02|控客轻智家轻宸超薄屏显开关四键mesh2.0|30930|
|ksmart.switch.sw4b01|KONKE四路智控开关|30867|
|kunton.plug.skwsg1|叶绿体智能墙壁插座|5707|
|kuxi.switch.sw1a01|酷犀智能开关一键|29363|
|kuxi.switch.sw2a01|酷犀智能开关二键|29364|
|kuxi.switch.sw3a01|酷犀智能开关三键|29365|
|kuxi.switch.sw3d01|酷犀情景智慧屏开关|32006|
|kuxi.switch.sw4a01|酷犀智能开关场景四键（带屏显）|29366|
|kuxi.switch.sw4a02|酷犀智能屏显开关四键Ultra|31171|
|kuxi.switch.sw4b01|酷犀智能开关四键|31711|
|kuxi.switch.sw4b02|酷犀智能屏显开关四键ProG|39138|
|kwi.switch.sw1a01|Kenwell 智能开关一键|30551|
|kwi.switch.sw2a01|Kenwell 智能开关二键|30552|
|kwi.switch.sw3a01|Kenwell 智能开关三键|30553|
|kwi.switch.sw4a01|Kenwell 智能开关四键|30554|
|kxng.switch.sw1a01|KNXG情景智能一键开关|39522|
|kxng.switch.sw2a01|KNXG情景智能二键开关|39523|
|kxng.switch.sw3a01|KNXG情景智能三键开关|39524|
|kxng.switch.sw4a01|KNXG情景智能四键开关|39525|
|laidun.switch.ldkg1|LD智能一路开关（Mesh2.0）|31125|
|laidun.switch.ldkg2|LD智能二路开关（Mesh2.0）|31126|
|laidun.switch.ldkg3|LD智能三路开关（Mesh2.0）|31127|
|laidun.switch.ldkg4|LD智能四路开关（Mesh2.0）|31128|
|laidun.switch.ldmtdq|LD智能通断器(Mesh2.0)|34353|
|laidun.switch.ldtdq2|LD智能通断器A(Mesh2.0)|34855|
|laig.plug.dttdq|小徕智能通断器（Mesh2.0）|31820|
|lat888.cs.ck01|迅为插卡取电器Mesh2.0|26847|
|lat888.switch.bln31|迅为一键智能开关Mesh2.0|26029|
|lat888.switch.bln32|迅为二键智能开关Mesh2.0|26030|
|lat888.switch.bln33|迅为三键智能开关Mesh2.0|26031|
|lat888.switch.bln34|迅为四键智能开关Mesh2.0|26032|
|lat888.switch.bln36|迅为六键智能开关Mesh2.0|26033|
|lcdq.switch.sw4a01|LC智能通断器|36879|
|ldzn.switch.sw1a01|凌动智能 单键开关2.0|25252|
|ldzn.switch.sw1c01|凌动智能 N9智能开关一键|35120|
|ldzn.switch.sw1d01|凌动智能 一键开关K2.0|36917|
|ldzn.switch.sw2a01|凌动智能 双键开关2.0|25253|
|ldzn.switch.sw2c01|凌动智能 N9智能开关二键|35121|
|ldzn.switch.sw2d01|凌动智能 二键开关K2.0|36918|
|ldzn.switch.sw3a01|凌动智能 三键开关2.0|25254|
|ldzn.switch.sw3a03|凌动智能 四寸屏显开关N9|36146|
|ldzn.switch.sw3c01|凌动智能 N9智能开关三键|35122|
|ldzn.switch.sw3d01|凌动智能 三键开关K2.0|36919|
|ldzn.switch.sw4a01|凌动智能 四键开关2.0|25255|
|ldzn.switch.sw4b01|凌动智能 四键开关K2.0|27668|
|ldzn.switch.sw4c01|凌动智能 N9智能开关四键|35123|
|leadzn.switch.ldys01|立德云数超薄屏显开关一键|28635|
|leadzn.switch.ldys02|立德云数超薄屏显开关二键|28636|
|leadzn.switch.ldys03|立德云数超薄屏显开关三键|28637|
|leadzn.switch.ldys4|立德云数4寸屏幕开关|29124|
|leelen.switch.bln31|LEELEN-P4一键智能开关|26869|
|leelen.switch.bln32|LEELEN-P4二键智能开关|26870|
|leelen.switch.bln33|LEELEN-P4三键智能开关|26871|
|legui.switch.sw1a01|乐归智能开关 一位|29029|
|legui.switch.sw2a01|乐归智能开关 二位|29030|
|legui.switch.sw3a01|乐归智能开关 三位|29031|
|legui.switch.sw4a01|乐归智能开关 四位|29032|
|legui.switch.ys4a02|乐归彩屏按键四位零火智能开关|36794|
|legui.switch.yw2a02|乐归彩屏按键二位零火智能开关|36792|
|legui.switch.yw3a02|乐归彩屏按键三位零火智能开关|36793|
|leike.switch.lkpxs1|雷克智能X2屏显一键开关|37318|
|leike.switch.lkpxs2|雷克智能X2屏显二键开关|37319|
|leike.switch.lkpxs3|雷克智能X2屏显三键开关|37320|
|leike.switch.sw1b01|雷克智能S1一键开关|37417|
|leike.switch.sw2b01|雷克智能S1二键开关|37418|
|leike.switch.sw3b01|雷克智能S1三键开关|37419|
|leike.switch.sw4b01|雷克智能S1四键开关|37420|
|lemesh.cs.swk01|HT插卡取电开关|12347|
|lemesh.remote.ts0|情景无线开关|16959|
|lemesh.remote.ts00|情景无线开关S|20809|
|lemesh.remote.ts1|八键无线情景开关|6742|
|lemesh.remote.ts10|情景旋钮遥控器Alpha|17658|
|lemesh.remote.ts4|情景无线旋钮开关K4|14456|
|lemesh.remote.ts5|情景无线开关K6|16747|
|lemesh.remote.ts6|情景无线开关K4|16748|
|lemesh.remote.ts7|情景无线开关K3|16956|
|lemesh.remote.ts8|情景无线开关K2|16957|
|lemesh.remote.ts9|情景无线开关K1|16958|
|lemesh.switch.sw0a01|情景mesh通断器|2007|
|lemesh.switch.sw0a02|情景Mesh通断器TM系列|3169|
|lemesh.switch.sw0a04|情景Mesh通断器V2S系列|13586|
|lemesh.switch.sw0c01|开关通断器C3版|12778|
|lemesh.switch.sw1a02|一键智能开关mesh版|3001|
|lemesh.switch.sw1f01|情景Mesh一键开关Pro|14470|
|lemesh.switch.sw1f11|情景Mesh一键开关Ultra|19379|
|lemesh.switch.sw1f20|情景Lemesh一键屏显开关Ultra|25737|
|lemesh.switch.sw1h01|HT一键智能开关mesh版|12768|
|lemesh.switch.sw2a02|二键智能开关mesh版|3000|
|lemesh.switch.sw2d02|情景智慧屏开关|16423|
|lemesh.switch.sw2e02|声必可智能开关屏|21914|
|lemesh.switch.sw2f01|情景Mesh二键开关Pro|14469|
|lemesh.switch.sw2f12|情景Mesh二键开关Ultra|19378|
|lemesh.switch.sw2f19|情景Lemesh二键屏显开关Ultra|25736|
|lemesh.switch.sw2h01|HT二键智能开关mesh版|12766|
|lemesh.switch.sw3a02|三键智能开关mesh版|2954|
|lemesh.switch.sw3b01|三键智能单火开关mesh版|7821|
|lemesh.switch.sw3f01|情景Mesh三键开关Pro|14468|
|lemesh.switch.sw3f13|情景Mesh三键开关Ultra|19377|
|lemesh.switch.sw3f18|情景Lemesh三键屏显开关Ultra|25004|
|lemesh.switch.sw3g01|情景Mesh一键开关V2S版|19816|
|lemesh.switch.sw3g02|情景Mesh二键开关V2S版|19815|
|lemesh.switch.sw3g03|情景Mesh三键开关V2S版|19093|
|lemesh.switch.sw3h01|HT三键智能开关mesh版|12765|
|lemesh.switch.sw4a02|四键智能开关mesh版|8194|
|lemesh.switch.sw4a03|HT六键智能开关mesh版|19769|
|lemesh.switch.sw4f01|情景Mesh四键开关Pro|14460|
|lemesh.switch.sw4f14|情景Mesh四键开关Ultra|18272|
|lemesh.switch.sw4f15|情景Lemesh四键屏显开关Ultra|23259|
|lemesh.switch.sw4f24|情景Lemesh四键屏显开关Pro|20011|
|lemesh.switch.sw4h01|HT四键智能开关Mesh版|12761|
|lemesh.switch.sw8a01|8键智能复合开关mesh版|8553|
|lesdn.switch.sw1a01|雷施顿智能开关（单键Mesh版）|28171|
|lesdn.switch.sw2a01|雷施顿智能开关（双键Mesh版）|28172|
|lesdn.switch.sw3a01|雷施顿智能开关（三键Mesh版）|28173|
|lesdn.switch.sw4a01|雷施顿智能开关（四键Mesh版）|28174|
|leshi.switch.sw1b01|一键轻触开关WiFi X1版|2238|
|leshi.switch.sw2b01|二键轻触开关WiFi X1版|2239|
|leshi.switch.sw3b01|三键轻触开关WiFi X1版|2240|
|leshi.switch.v0001|3位智慧开关WIFI X版|1483|
|leshi.switch.v0002|2位智慧开关WIFI X1版|2034|
|leshi.switch.v0003|1位智慧开关WIFI X1版|2035|
|leshi.switch.v0004|3位智慧开关WIFI X1版|2382|
|leshi.switch.v002|开关通断器WIFI X版|1581|
|lex.switch.sw1b01|LEXMesh 一键智能开关2.0|27601|
|lex.switch.sw2b01|LEXMesh 二键智能开关2.0|25292|
|lex.switch.sw3b01|LEXMesh 三键智能开关2.0|25294|
|lex.switch.sw4a02|LEXMesh 四键中间屏显开关2.0|27434|
|lex.switch.sw4b01|LEXMesh 四键智能开关2.0|25295|
|lgb.plug.lgb002|巧旺智能插座|23504|
|lgb.plug.lgbear|巧旺智能排插|23478|
|lh2024.switch.sw1a01|留虹照明智能开关一键|31946|
|lh2024.switch.sw2a01|留虹照明智能开关二键|31947|
|lh2024.switch.sw3a01|留虹照明智能开关三键|31948|
|lh2024.switch.sw4a01|留虹照明智能开关四键|31949|
|lhz.remote.2g|罗格朗二位场景开关MESH版|16924|
|lhz.remote.4g|罗格朗四位场景开关MESH版|16927|
|lhz.remote.4gang|罗格朗逸景Plus四位场景开关|26276|
|lhz.remote.6g|罗格朗六位场景开关MESH版|16928|
|lhz.remote.jy4g|罗格朗简悦四位零火场景开关|29961|
|lhz.remote.qy4g|罗格朗绮蕴四位零火场景开关|31565|
|lhz.remote.sw6a02|罗格朗智绘六位零火场景开关|29055|
|lhz.remote.sw6d01|罗格朗维翼六位零火场景开关|34294|
|lhz.switch.1g|罗格朗一位带零线智能开关MESH版|16929|
|lhz.switch.1gang|罗格朗一位带零线智能开关|11615|
|lhz.switch.2g|罗格朗二位带零线智能开关MESH版|16930|
|lhz.switch.2gang|罗格朗二位带零线智能开关|11616|
|lhz.switch.3g|罗格朗三位带零线智能开关MESH版|16931|
|lhz.switch.3gang|罗格朗三位带零线智能开关|11617|
|lhz.switch.jy1g|罗格朗简悦一位智能开关|29960|
|lhz.switch.jy2g|罗格朗简悦二位智能开关|29959|
|lhz.switch.jy3g|罗格朗简悦三位智能开关|29958|
|lhz.switch.jy4g01|罗格朗简悦四位智能开关|31230|
|lhz.switch.qy1g01|罗格朗绮蕴一位智能开关|31401|
|lhz.switch.qy2g01|罗格朗绮蕴二位智能开关|31402|
|lhz.switch.qy3g01|罗格朗绮蕴三位智能开关|31403|
|lhz.switch.qy4g01|罗格朗绮蕴四位智能开关|31404|
|lhz.switch.sw1a01|罗格朗智绘一位智能开关|28332|
|lhz.switch.sw1c03|罗格朗维翼一位彩屏智能开关Pro|38642|
|lhz.switch.sw1d01|罗格朗维翼一位智能开关|34288|
|lhz.switch.sw1g|罗格朗逸景Plus一位智能开关|26307|
|lhz.switch.sw2a01|罗格朗智绘二位智能开关|28333|
|lhz.switch.sw2c01|罗格朗维翼二位彩屏智能开关|34078|
|lhz.switch.sw2c03|罗格朗维翼二位彩屏智能开关Pro|38643|
|lhz.switch.sw2d01|罗格朗维翼二位智能开关|34289|
|lhz.switch.sw2g|罗格朗逸景Plus二位智能开关|26306|
|lhz.switch.sw3a01|罗格朗智绘三位智能开关|28334|
|lhz.switch.sw3a03|罗格朗四寸智能触控屏开关|38184|
|lhz.switch.sw3c01|罗格朗维翼三位彩屏智能开关|34077|
|lhz.switch.sw3c03|罗格朗维翼三位彩屏智能开关Pro|38644|
|lhz.switch.sw3d01|罗格朗维翼三位智能开关|34291|
|lhz.switch.sw3g|罗格朗逸景Plus三位智能开关|25685|
|lhz.switch.sw4a01|罗格朗智绘四位智能开关|28335|
|lhz.switch.sw4c01|罗格朗维翼四位彩屏智能开关|34076|
|lhz.switch.sw4c03|罗格朗维翼四位彩屏智能开关Pro|38645|
|lhz.switch.sw4d01|罗格朗维翼四位智能开关|34292|
|lhz.switch.sw4g|罗格朗逸景Plus四位智能开关|26853|
|line.plug.afsb1|方舟鱼智能断路器D1|17781|
|line.plug.lhbl7|方舟鱼智能断路器D2|17827|
|line.remote.fwkge2|方舟鱼无线开关E2|30883|
|line.remote.fxnkg|LineHope智能无线旋钮开关E6|21805|
|line.remote.kge1s|方舟鱼无线开关E1S|26623|
|line.remote.wkgf1|方舟鱼无线开关E1|15249|
|line.remote.xnkg01|TATACASA智能无线旋钮开关AI-001|21803|
|line.switch.fkgh41|方舟鱼智能墙壁开关H4（零火单键版）|13929|
|line.switch.fkgh42|方舟鱼智能墙壁开关H4（零火双键版）|13930|
|line.switch.fkgh43|方舟鱼智能墙壁开关H4（零火三键版）|13931|
|line.switch.fkgh44|方舟鱼智能墙壁开关H4（零火四键版）|13932|
|line.switch.h11|LineHope智能墙壁开关H1（零火单键版）|11679|
|line.switch.h12|LineHope智能墙壁开关H1（零火双键版）|11680|
|line.switch.h13|LineHope智能墙壁开关H1（零火三键版）|11681|
|line.switch.kgdh51|方舟鱼智能墙壁开关H5 单键|21806|
|line.switch.kgdh52|方舟鱼智能墙壁开关H5 双键|21807|
|line.switch.kgdh53|方舟鱼智能墙壁开关H5 三键|21808|
|line.switch.kgdh54|方舟鱼智能墙壁开关H5 四键|22766|
|line.switch.kgh41|LineHope智能墙壁开关H4（零火单键版）|13490|
|line.switch.kgh42|LineHope智能墙壁开关H4（零火双键版）|13491|
|line.switch.kgh43|LineHope智能墙壁开关H4（零火三键版）|13492|
|line.switch.kgh44|LineHope智能墙壁开关H4（零火四键版）|13493|
|line.switch.kgh81|LineHope智能墙壁开关H8 单键|23709|
|line.switch.kgh82|LineHope智能墙壁开关H8 双键|23754|
|line.switch.kgh83|LineHope智能墙壁开关H8 三键|23755|
|line.switch.kgk1|LineHope智能墙壁开关K1（零火单键版）|6559|
|line.switch.kgk12|LineHope智能墙壁开关K1（零火双键版）|6560|
|line.switch.kgk13|LineHope智能墙壁开关K1（零火三键版）|6561|
|line.switch.pkge81|LineHope智能屏显开关E8 单键|23576|
|line.switch.pkge82|LineHope智能屏显开关E8 双键|23575|
|line.switch.pkge83|LineHope智能屏显开关E8 三键|23574|
|line.switch.pxkge8|LineHope智能屏显开关E8 四键|23372|
|line.switch.sw2a02|方舟鱼智能柜开关D3|32310|
|line.switch.zbgkg|志邦家居智能柜控制开关M25001|26200|
|linju.plug.ljspm2|聆巨智能插座（Mesh2.0）|25301|
|linju.plug.sw6a01|聆巨六路智能排插（Mesh）|18058|
|linju.plug.znkzq|聆巨智能控制器|17610|
|linju.switch.sw0a01|聆巨蓝牙Mesh通断器|12261|
|linp.remote.k9b|领普蓝牙无线开关（三键）|3581|
|linp.remote.k9b01|领普无线开关K11|7184|
|linp.remote.k9b1|领普蓝牙无线开关（单键）|5480|
|linp.remote.k9b11|领普蓝牙无线开关（双键）|5481|
|linp.remote.kh1bb1|领普无线开关KH1（单键）|9843|
|linp.remote.kh1bb2|领普无线开关KH1（双键）|9842|
|linp.remote.kh1bb3|领普无线开关KH1（三键）|9841|
|linp.remote.kh1bb4|领普无线开关KH1（四键）|9630|
|linp.remote.ks1|领普无线开关KS1|14945|
|linp.switch.e2db1|领普智能屏显开关（零火MESH 一键）|15866|
|linp.switch.e2db2|领普智能屏显开关（零火MESH 二键）|15865|
|linp.switch.e2db3|领普智能屏显开关（零火MESH三键）|15864|
|linp.switch.e3sbw1|领普单火智能墙壁开关（MESH2.0 单键）|29424|
|linp.switch.e3sbw2|领普单火智能墙壁开关（MESH2.0 双键）|29442|
|linp.switch.e3sbw3|领普单火智能墙壁开关（MESH2.0 三键）|29447|
|linp.switch.e5dbw1|领普超薄智能屏显开关（MESH2.0 单键）|31974|
|linp.switch.e5dbw2|领普超薄智能屏显开关（MESH2.0 双键）|31975|
|linp.switch.e5dbw3|领普超薄智能屏显开关（MESH2.0 三键）|31357|
|linp.switch.e5dbw4|领普超薄智能屏显开关（MESH2.0 四键）|31976|
|linp.switch.h3dbw1|领普智能彩屏开关（单键）|37459|
|linp.switch.h3dbw2|领普智能彩屏开关（双键）|37460|
|linp.switch.h3dbw3|领普智能彩屏开关（三键）|37461|
|linp.switch.pxdbw1|领普智能屏显开关（MESH2.0 单键）|26192|
|linp.switch.pxdbw2|领普智能屏显开关（MESH2.0 双键）|26191|
|linp.switch.pxdbw3|领普智能屏显开关（MESH2.0 三键）|26172|
|linp.switch.q31|领普墙壁开关（单键）|1852|
|linp.switch.q31s|领普Q3墙壁开关(单键)|3190|
|linp.switch.q32|领普墙壁开关（双键）|1851|
|linp.switch.q32s|领普Q3墙壁开关(双键)|3191|
|linp.switch.q33|领普墙壁开关（三键）|1853|
|linp.switch.q33s|领普Q3墙壁开关(三键)|3192|
|linp.switch.q3s1|领普墙壁开关MESH（单键）|2428|
|linp.switch.q3s2|领普墙壁开关MESH（双键）|2429|
|linp.switch.q3s3|领普墙壁开关MESH（三键）|2274|
|linp.switch.q4s1|领普单火墙壁开关MESH（单键）|5043|
|linp.switch.q4s2|领普单火墙壁开关MESH（双键）|5044|
|linp.switch.q4s3|领普单火墙壁开关MESH（三键）|5045|
|linp.switch.qh1db1|领普墙壁开关QH1（MESH单键）|9787|
|linp.switch.qh1db2|领普墙壁开关QH1（MESH双键）|9786|
|linp.switch.qh1db3|领普墙壁开关QH1（MESH三键）|9785|
|linp.switch.qh1db4|领普墙壁开关QH1（MESH四键）|9452|
|linp.switch.qh1dp1|智能墙壁开关QH1（单键PLC版）|76842|
|linp.switch.qh1dp2|智能墙壁开关QH1（双键PLC版）|76859|
|linp.switch.qh1dp3|智能墙壁开关QH1（三键PLC版）|76858|
|linp.switch.qh1dp4|智能墙壁开关QH1（四键PLC版）|76857|
|linp.switch.qh2db2|领普墙壁开关H2（零火MESH 两键）|16806|
|linp.switch.qh2db4|领普墙壁开关H2（零火MESH 四键）|16807|
|linp.switch.qh2db8|领普墙壁开关H2（零火MESH 八键）|16808|
|linp.switch.qt1db1|领普墙壁开关QT1（零火MESH一键）|15658|
|linp.switch.qt1db2|领普墙壁开关QT1（零火MESH二键）|15659|
|linp.switch.qt1db3|领普墙壁开关QT1（零火MESH三键）|15660|
|linp.switch.qt1db4|领普墙壁开关QT1（零火MESH四键）|15661|
|linp.switch.s1|领普全面屏开关|73833|
|linp.switch.s2dw3|领普触屏开关S2|17582|
|linp.switch.s3dw|领普中控屏开关S3|22234|
|linp.switch.s5db|领普超薄触屏开关（MESH2.0）|30706|
|linp.switch.t2dbw1|领普智能墙壁开关（单键）|23474|
|linp.switch.t2dbw2|领普智能墙壁开关（双键）|23473|
|linp.switch.t2dbw3|领普智能墙壁开关（三键）|23310|
|linp.switch.t2dbw4|领普智能墙壁开关（四键）|26373|
|linp.switch.t2dsb1|领普低功耗智能开关（单键）|37767|
|linp.switch.t2dsb2|领普低功耗智能开关（双键）|37768|
|linp.switch.t2dsb3|领普低功耗智能开关（三键）|37769|
|linp.switch.t2dsb4|领普低功耗智能开关（四键）|37770|
|linp.switch.wq4db1|零火智能墙壁开关（MESH 单键）|12136|
|linp.switch.wq4db2|零火智能墙壁开关（MESH 双键）|12135|
|linp.switch.wq4db3|零火智能墙壁开关（MESH 三键）|12131|
|linp.switch.wq4sb1|单火智能墙壁开关（MESH 单键）|12291|
|linp.switch.wq4sb2|单火智能墙壁开关（MESH 双键）|12292|
|linp.switch.wq4sb3|单火智能墙壁开关（MESH 三键）|12293|
|linp.switch.xh1dp|智能旋钮开关XH1 (PLC版)|76870|
|lkzm.switch.sw1a01|雷卡之星智能开关一键|31942|
|lkzm.switch.sw2a01|雷卡之星智能开关二键|31943|
|lkzm.switch.sw3a01|雷卡之星智能开关三键|31944|
|lkzm.switch.sw4a01|雷卡之星智能开关四键|31945|
|lmyd.switch.sw1a01|吉帝创S7系列零火智能一键开关|32940|
|lmyd.switch.sw2a01|吉帝创S7系列零火智能二键开关|32939|
|lmyd.switch.sw3a01|吉帝创S7系列零火智能三键开关|32938|
|lmyd.switch.sw4a01|吉帝创S7系列零火智能四键开关|34199|
|longs.switch.lsnls1|龙胜一位零火开关|20172|
|longs.switch.lsnls2|龙胜二位零火开关|20173|
|longs.switch.lsnls3|龙胜三位零火开关|20174|
|longs.switch.lsnls4|龙胜四位零火开关|20175|
|longs.switch.nlsw21|龙胜一位零火屏显开关|29258|
|longs.switch.nlsw22|龙胜二位零火屏显开关|29259|
|longs.switch.nlsw23|龙胜三位零火屏显开关|29260|
|longs.switch.nlsw24|龙胜四位零火屏显开关|29261|
|longs.switch.nlsw3d|龙胜圆屏智能多功能面板|29262|
|longs.switch.nlsw4z|龙胜全面屏智能面板|29263|
|longs.switch.yls01|龙胜一位彩屏按键零火开关|38436|
|longs.switch.yls02|龙胜二位彩屏按键零火开关|38437|
|longs.switch.yls03|龙胜三位彩屏按键零火开关|38438|
|longs.switch.yls04|龙胜四位彩屏按键零火开关|38439|
|lonink.switch.ln064|LONINK智能一键开关 WiFi|71108|
|lonink.switch.ln065|LONINK智能二键开关 WiFi|71109|
|lonink.switch.ln066|LONINK智能三键开关 WiFi|71110|
|lonink.switch.ln084|LONINK一键开关（WiFi）|69343|
|lonink.switch.ln085|LONINK二键开关（WiFi）|69450|
|lonink.switch.ln086|LONINK三键开关（WiFi）|68476|
|lqdc88.switch.dcwtdq|电传智能通断器（WiFi）|34445|
|lrn.switch.sw2a01|LRN思维科高低压双路开关|18772|
|lumi.ctrl_86plug.aq1|Aqara墙壁插座（ZigBee版）|611|
|lumi.ctrl_86plug.v1|墙壁插座(ZigBee版)|355|
|lumi.ctrl_ln1.aq1|Aqara 墙壁开关（零火线单键版）|609|
|lumi.ctrl_ln1.v1|Aqara墙壁开关（零火线单键版）|357|
|lumi.ctrl_ln2.aq1|Aqara墙壁开关（零火线双键版）|610|
|lumi.ctrl_ln2.v1|Aqara墙壁开关（零火线双键版）|356|
|lumi.ctrl_neutral1.v1|Aqara 墙壁开关(单火线单键版)|96|
|lumi.ctrl_neutral2.v1|Aqara 墙壁开关(单火线双键版)|93|
|lumi.plug.n03|Aqara 86 型智能墙壁插座H1|71323|
|lumi.relay.c2acn01|Aqara双路控制模块|714|
|lumi.remote.acn003|Aqara无线开关 E1 (贴墙式单键版)|72356|
|lumi.remote.acn004|Aqara无线开关 E1 (贴墙式双键版)|72357|
|lumi.remote.acn007|Aqara无线开关 E1|73033|
|lumi.remote.b186acn01|Aqara无线开关(贴墙式单键版)|65556|
|lumi.remote.b186acn02|Aqara无线开关 D1（贴墙式单键版）|66631|
|lumi.remote.b1acn01|Aqara无线开关|805|
|lumi.remote.b286acn01|Aqara 无线开关（贴墙式双键版）|65557|
|lumi.remote.b286acn02|Aqara无线开关 D1（贴墙式双键版）|66630|
|lumi.remote.b286opcn01|无线场景开关(双键版)|66828|
|lumi.remote.b486opcn01|无线场景开关(四键版)|66827|
|lumi.remote.b686opcn01|无线场景开关(六键版)|66826|
|lumi.remote.mcn001|小米无线开关（蓝牙版）|9095|
|lumi.sensor_cube.aqgl01|Aqara魔方控制器|711|
|lumi.sensor_cube.v1|魔方控制器|95|
|lumi.sensor_switch.aq2|Aqara无线开关|452|
|lumi.sensor_switch.aq3|Aqara无线开关（升级版）|586|
|lumi.sensor_switch.v1|无线开关|41|
|lumi.sensor_switch.v2|小米无线开关|62|
|lumi.switch.acn016|小米智能开关（单开 零火版）|6379|
|lumi.switch.acn017|小米智能开关（双开 零火版）|6380|
|lumi.switch.acn018|小米智能开关（三开 零火版）|6381|
|lumi.switch.acn032|Aqara 妙控开关 S1E|74667|
|lumi.switch.acn040|Aqara 智能墙壁开关（零火线三键版）|75916|
|lumi.switch.acn048|Aqara卡农 智能墙壁开关 Z1（单键版）|77968|
|lumi.switch.acn049|Aqara卡农 智能墙壁开关 Z1（双键版）|77969|
|lumi.switch.acn054|Aqara卡农 智能墙壁开关 Z1（三键版）|77970|
|lumi.switch.acn055|Aqara卡农 智能墙壁开关 Z1（四键版）|77971|
|lumi.switch.b1lacn02|Aqara智能墙壁开关 D1（单火线单键版）|66642|
|lumi.switch.b1lc04|Aqara 智能墙壁开关（单火线单键版）|71636|
|lumi.switch.b1nacn02|Aqara智能墙壁开关 D1（零火线单键版）|66640|
|lumi.switch.b1nc01|Aqara 智能墙壁开关（零火线单键版）|71638|
|lumi.switch.b2lacn02|Aqara智能墙壁开关 D1（单火线双键版）|66641|
|lumi.switch.b2lc04|Aqara 智能墙壁开关（单火线双键版）|71637|
|lumi.switch.b2nacn02|Aqara智能墙壁开关 D1（零火线双键版）|66639|
|lumi.switch.b2nc01|Aqara 智能墙壁开关（零火线双键版）|71639|
|lumi.switch.l3acn3|Aqara智能墙壁开关 D1（单火线三键版）|67859|
|lumi.switch.n0acn2|单路控制模块 T1（零火线版）|68017|
|lumi.switch.n1eic1|ES墙壁开关（零火单键版）|69574|
|lumi.switch.n1eic2|ES场景开关（零火单键版）|69579|
|lumi.switch.n2eic1|ES墙壁开关（零火双键版）|69575|
|lumi.switch.n2eic2|ES场景开关（零火双键版）|69580|
|lumi.switch.n3acn3|Aqara智能墙壁开关 D1（零火线三键版）|67858|
|lumi.switch.n3eic1|ES墙壁开关（零火三键版）|69576|
|lumi.switch.n3eic2|ES场景开关（零火三键版）|69581|
|lumi.switch.n4eic1|ES墙壁开关（零火四键版）|69577|
|lumi.switch.n4eic2|ES场景开关（零火四键版）|69582|
|lumi.switch.n6eic1|ES墙壁开关（零火六键版）|69578|
|lumi.switch.n6eic2|ES场景开关（零火六键版）|69583|
|luoban.switch.sw0a01|LB智能通断器|36999|
|luoban.switch.sw1a01|DXV一键开关Mesh2.0版|29868|
|luoban.switch.sw1c01|LB一位智能开关|37151|
|luoban.switch.sw2a01|DXV二键开关Mesh2.0版|29867|
|luoban.switch.sw2c01|LB二位智能开关|37152|
|luoban.switch.sw3a01|DXV三键开关Mesh2.0版|29866|
|luoban.switch.sw3a03|LB全面屏开关|36672|
|luoban.switch.sw3c01|LB三位智能开关|37153|
|luoban.switch.sw4a01|DXV四键开关Mesh2.0版|29698|
|luoban.switch.sw4a02|LB四位屏显智能开关|34631|
|luoban.switch.sw4c01|LB四位智能开关|37154|
|lvgmbh.switch.ldws1|朗德万斯智能开关（一开）|39967|
|lvgmbh.switch.ldws2|朗德万斯智能开关（二开）|39968|
|lvgmbh.switch.ldws3|朗德万斯智能开关（三开）|39969|
|lvgmbh.switch.ldws4|朗德万斯智能开关（四开）|39970|
|lxun.cs.ckqd01|智能插卡取电mesh版|11987|
|lxun.remote.wxkg08|联讯智能无线开关|13613|
|lxun.switch.bln31|LX智能一键开关C5-Mesh版|24833|
|lxun.switch.bln32|LX智能二键开关C5-Mesh版|24834|
|lxun.switch.bln33|LX智能三键开关C5-Mesh版|24835|
|lxun.switch.bln34|LX智能四键开关C5-Mesh版|24836|
|lxun.switch.c61k|LX智能一键开关C6-Mesh版|29758|
|lxun.switch.c62k|LX智能二键开关C6-Mesh版|29759|
|lxun.switch.c63k|LX智能三键开关C6-Mesh版|29760|
|lxun.switch.c64k|LX智能四键开关C6-Mesh版|29761|
|lxun.switch.lxkg1|LX智能一位开关M6(Mesh2.0)|31041|
|lxun.switch.lxkg2|LX智能二位开关M6(Mesh2.0)|31040|
|lxun.switch.lxkg3|LX智能三位开关M6(Mesh2.0)|31039|
|lxun.switch.lxkg4|LX智能四位开关M6(Mesh2.0)|31038|
|lxun.switch.lxkgm1|智能开关-三键mesh版|10529|
|lxun.switch.lxnsw3|LX智能开关-三键BLE-Mesh版|20429|
|lxun.switch.lxswm1|智能开关-一键mesh版|11288|
|lxun.switch.lxswm2|智能开关-二键mesh版|11287|
|lxun.switch.lxswm4|智能开关-四键mesh版|11253|
|lxun.switch.sw08|智能8键复合开关mesh版|12987|
|lxun.switch.tdq01|智能通断器mesh版|11847|
|lxzn.switch.01|轻触1键零火开关 （蓝牙mesh）|16440|
|lxzn.switch.02|轻触2键零火开关 （蓝牙mesh）|16470|
|lxzn.switch.03|轻触3键零火开关 （蓝牙mesh）|16474|
|lxzn.switch.cbcsmj|Wi-Fi智能通断器L1|16481|
|lyzndq.switch.sw0a01|RWRW 智能高低压情景通断器|41062|
|lyzndq.switch.sw1a01|RWRW 一键智能开关2.0|32103|
|lyzndq.switch.sw2a01|RWRW 二键智能开关2.0|32104|
|lyzndq.switch.sw2a02|RWRW 高低压双路开关2.0|32180|
|lyzndq.switch.sw3a01|RWRW 三键智能开关2.0|32105|
|lyzndq.switch.sw4a01|RWRW 四键智能开关2.0|32106|
|lyzndq.switch.sw4a02|RWRW 四键智能屏显开关2.0|32194|
|lzmesh.remote.sw1b01|朗尊旋钮无线开关T1|23793|
|lzmesh.remote.sw1b02|朗尊旋钮无线开关T3|28904|
|lzmesh.remote.sw2b01|朗尊手柄无线开关T2|23794|
|lzmesh.remote.sw4g01|Langzun  无线智能四键旋钮开关|40175|
|lzmesh.switch.bln31|列科玛一位智能开关（零火版）|22264|
|lzmesh.switch.bln32|列科玛二位智能开关（零火版）|22265|
|lzmesh.switch.bln33|列科玛三位智能开关（零火版）|22266|
|lzmesh.switch.bln34|列科玛四位智能开关（零火版）|22267|
|lzmesh.switch.sw1a01|朗尊MESH一位智能开关|23789|
|lzmesh.switch.sw1b01|朗尊MESH2.0一位多功能智能开关|29567|
|lzmesh.switch.sw1f01|朗尊｜蓝牙MESH2.0 一位智能开关|38413|
|lzmesh.switch.sw2a01|朗尊MESH二位智能开关|23790|
|lzmesh.switch.sw2b01|朗尊MESH2.0二位多功能智能开关|29568|
|lzmesh.switch.sw2c01|朗尊 MESH2.0 M系列 二键智能开关|33458|
|lzmesh.switch.sw2f01|朗尊｜蓝牙MESH2.0 二位智能开关|38412|
|lzmesh.switch.sw3a01|朗尊MESH三位智能开关|23791|
|lzmesh.switch.sw3b01|朗尊MESH2.0三位多功能智能开关|29569|
|lzmesh.switch.sw3f01|朗尊｜蓝牙MESH2.0 三位智能开关|38411|
|lzmesh.switch.sw4a01|朗尊MESH四位智能开关|23792|
|lzmesh.switch.sw4a02|朗尊四键屏显开关PRO|28099|
|lzmesh.switch.sw4b01|朗尊MESH2.0四位多功能智能开关|29570|
|lzmesh.switch.sw4c01|朗尊 MESH2.0 M系列 四键智能开关|33459|
|lzmesh.switch.sw4f01|朗尊｜蓝牙MESH2.0 四位智能开关|38410|
|manew.switch.sw1a01|思码光智雅一键智能开关|31526|
|manew.switch.sw2a01|思码光智雅二键智能开关|31525|
|manew.switch.sw3a01|思码光智雅三键智能开关|31524|
|manew.switch.sw4a01|思码光智雅四键屏显智能开关|31523|
|mcl.switch.1k|小妍灯控开关（单开）|12414|
|mcl.switch.2k|小妍灯控开关（双开）|12413|
|mcl.switch.3k|小妍灯控开关（三开）|12412|
|mcolor.switch.sw1a01|MCOLOR智能开关 零火单键|29834|
|mcolor.switch.sw1b01|MCOLOR智能开关 智灵一键|36586|
|mcolor.switch.sw2a01|MCOLOR智能开关 零火双键|29908|
|mcolor.switch.sw2b01|MCOLOR智能开关 智灵二键|36587|
|mcolor.switch.sw3a01|MCOLOR智能开关 零火三键|29909|
|mcolor.switch.sw3a03|MCOLOR 智能开关全面屏|34333|
|mcolor.switch.sw3b01|MCOLOR智能开关 智灵三键|36588|
|mcolor.switch.sw4a01|MCOLOR智能开关 零火四键|29910|
|mcolor.switch.sw4b01|MCOLOR智能开关 智灵四键|36589|
|mcolor.switch.sw8a02|MCOLOR智能开关 零火八键|35184|
|mcosu.switch.pipaf1|F1 MESH一位开关|12032|
|mcosu.switch.pipaf2|F1 MESH二位开关|12033|
|mcosu.switch.pipaf3|F1 MESH三位开关|12034|
|mcosu.switch.pipaf4|F1 MESH四位开关|12035|
|mcosu.switch.pipam1|PIPA智能一键开关MESH|7609|
|mcosu.switch.pipam2|PIPA智能二键开关MESH|7610|
|mcosu.switch.pipam3|PIPA智能三键开关MESH|7611|
|melion.switch.bm6a1|美莱恩调光开关|26286|
|melion.switch.sw1a01|美莱恩智能开关（单键）|32133|
|melion.switch.sw2a01|美莱恩智能开关（双键）|32132|
|melion.switch.sw3a01|美莱恩智能开关（三键）|32131|
|melion.switch.sw4a01|美莱恩智能开关（四键）|32130|
|melion.switch.sw6a01|美莱恩智能开关（六键）|32116|
|merryt.switch.sw2a01|迈睿双路通断器S2|33335|
|merten.switch.mdkg1|ZM智能单键复合开关|34132|
|merten.switch.mdkg2|ZM智能双键复合开关|34131|
|merten.switch.mdkg3|ZM智能三键复合开关|34130|
|merten.switch.mdkg4|ZM智能四键复合开关|34129|
|merten.switch.mdkg6|ZM智能六键复合开关|36948|
|merten.switch.mdkg8|ZM智能八键复合开关|36952|
|mexin.switch.bldup1|美心智能一键开关|37469|
|mexin.switch.bldup2|美心智能二键开关|37470|
|mexin.switch.bldup3|美心智能三键开关|37471|
|mexin.switch.bldup4|美心智能四键开关|37472|
|mihua.plug.rcw01|光电蜂电脑开机卡|25239|
|miir.remote.ir01|自定义遥控|65714|
|miot.plug.021|服务单更新验证1|78513|
|miot.plug.v1640|MIOT内部测试model，非实际上线产品，勿动。|330|
|miot.switch.mswl1|Mesh无线开关测试(单键)|5985|
|miot.switch.mswl2|Mesh无线开关测试(双键)|5984|
|miot.switch.mswl3|Mesh无线开关测试(三键)|5974|
|miot.switch.spec|标准插件HOOK设备（删除会影响线上所有插件运行，千万勿删，非常重要）|6479|
|miot.switch.y0715|测试产品|6446|
|mitch.switch.sw4a02|慧电熊四路超级屏显开关(Mesh2.0)|35129|
|mjkj.switch.jmp001|即米智能屏显开关(一位)|32156|
|mjkj.switch.jmp002|即米智能屏显开关(二位)|32157|
|mjkj.switch.jmp003|即米智能屏显开关(三位)|32158|
|mjkj.switch.jmp004|即米智能屏显开关(四位)|32159|
|mjkj.switch.jmy001|即米智能屏显圆屏开关|32160|
|mjkj.switch.l15k2|BUBA智能开关二键(PLC)|82060|
|mjkj.switch.l15k4|BUBA智能开关四键(PLC)|82061|
|mjkj.switch.l15k8|BUBA智能开关八键(PLC)|82062|
|mjkj.switch.sw1a01|即米智能开关（一键）|22300|
|mjkj.switch.sw1a02|即米智能开关Pro一键|29740|
|mjkj.switch.sw2a01|即米智能开关（二键）|22301|
|mjkj.switch.sw2a02|即米智能开关Pro二键|29741|
|mjkj.switch.sw3a01|即米智能开关(三键)|22302|
|mjkj.switch.sw3a02|即米智能开关Pro三键|29742|
|mjkj.switch.sw3d01|即米智能屏幕开关|32053|
|mjkj.switch.sw4a01|即米智能开关(四键）|22303|
|mjkj.switch.sw4a02|即米智能开关Pro四键|29743|
|mjkj.switch.v9is1|即米智能开关Air（一位）|31679|
|mjkj.switch.v9is2|即米智能开关Air（二位）|31680|
|mjkj.switch.v9is3|即米智能开关Air（三位）|31681|
|mjkj.switch.v9is4|即米智能开关Air（四位）|31682|
|mkit.switch.sw0a01|ABKY通断器Mesh2.0|37125|
|mlianj.switch.bln31|MLIANJIA智慧Ai一键屏显开关|27130|
|mlianj.switch.bln32|MLIANJIA智慧Ai二键屏显开关|27131|
|mlianj.switch.bln33|MLIANJIA智慧Ai三键屏显开关|27132|
|mlianj.switch.bln34|MLIANJIA智慧Ai四键屏显开关|27133|
|mlianj.switch.bln36|MLIANJIA智慧Ai六键屏显开关|27134|
|mlianj.switch.bpx3|MLIANJIA智慧Ai屏幕开关|28483|
|mlszm.switch.mlsb1|MLS未来一位开关B1|38533|
|mlszm.switch.mlsb2|MLS未来二位开关B2|38534|
|mlszm.switch.mlsb3|MLS未来三位开关B3|38535|
|mlszm.switch.mlsb4|MLS未来四位开关B4|38536|
|mlszm.switch.mlsd1|MLS数显一位开关D1|38525|
|mlszm.switch.mlsd2|MLS数显二位开关D2|38526|
|mlszm.switch.mlsd3|MLS数显三位开关D3|38527|
|mlszm.switch.mlsd4|MLS数显四位开关D4|38528|
|mlszm.switch.mlsq1|MLS致典一位开关Q1|38529|
|mlszm.switch.mlsq2|MLS致典二位开关Q2|38530|
|mlszm.switch.mlsq3|MLS致典三位开关Q3|38531|
|mlszm.switch.mlsq4|MLS致典四位开关Q4|38532|
|mlszm.switch.sw3a01|木林森Z01智能中控屏开关|18701|
|mlszn.plug.pc01|木林森智能轨道插座|38839|
|mlszn.switch.sw1a01|木林森智能一键开关（竖版）|36333|
|mlszn.switch.sw1b01|木林森智能一键开关（田字版）|36406|
|mlszn.switch.sw1c01|木林森木系列一键开关|40467|
|mlszn.switch.sw2a01|木林森智能二键开关（竖版）|36334|
|mlszn.switch.sw2b01|木林森智能二键开关（田字版）|36407|
|mlszn.switch.sw2c01|木林森木系列二键开关|40468|
|mlszn.switch.sw3a01|木林森智能三键开关（竖版）|36335|
|mlszn.switch.sw3b01|木林森智能三键开关（田字版）|36408|
|mlszn.switch.sw3c01|木林森木系列三键开关|40469|
|mlszn.switch.sw4a01|木林森智能四键开关（竖版）|36336|
|mlszn.switch.sw4b01|木林森智能四键开关（田字版）|36409|
|mlszn.switch.sw4c01|木林森木系列四键开关|40470|
|mly.switch.sw0a01|魔力云智能灯光控制器|6865|
|mly.switch.sw1a01|魔力云一开智能开关|6075|
|mly.switch.sw2a01|魔力云二开智能开关|6073|
|mly.switch.sw3a01|魔力云三开智能开关|6072|
|mmdq.switch.bln31|MM一位扩展智能开关|22337|
|mmdq.switch.bln32|MM二位扩展智能开关|22338|
|mmdq.switch.bln33|MM三位扩展智能开关|22339|
|mmdq.switch.bln34|MM四位扩展智能开关|22340|
|msuen.switch.czc20|水享智能阀|11090|
|msuen.switch.czc20s|水享手动辅助智能阀|11092|
|murong.remote.mrk009|慕容柯无线开关|33272|
|murong.switch.mrk002|慕容柯隐形开关灵动版|14297|
|murong.switch.mrk005|慕容柯隐形开关Mesh2.0|20998|
|mypile.switch.sw5a01|MyPile智能壁挂充电支架|19621|
|naner.controller.86m|南尔智能音乐中控主机|74469|
|nanfu.remote.nl2v4|南福智能开关 NIF-D2K4|11056|
|nbjy.switch.h4p|俊頤智能开关H4 Plus(屏显免刻字)|35466|
|nbxh.remote.sw1b02|JOCO智能K1情景旋钮无线开关|39024|
|nbxh.switch.jckg1|JOCO智能自然系列一路开关（Mesh2.0）|29520|
|nbxh.switch.jckg2|JOCO智能自然系列二路开关（Mesh2.0）|29519|
|nbxh.switch.jckg3|JOCO智能自然系列三路开关（Mesh2.0）|29518|
|nbxh.switch.jckg4|JOCO智能自然系列四路开关（Mesh2.0）|29517|
|nbxh.switch.jckg5|JOCO四键圆屏开关（Mesh2.0）|30566|
|nbxh.switch.jckg6|JOCO智能X1八键开关  （Mesh2.0）|30584|
|nbxh.switch.sw1a01|JOCO智能Mesh一键开关|24946|
|nbxh.switch.sw1b01|JOCO智能Mesh一键屏显开关|25609|
|nbxh.switch.sw2a01|JOCO智能Mesh二键开关|24947|
|nbxh.switch.sw2b01|JOCO智能Mesh二键屏显开关|25608|
|nbxh.switch.sw3a01|JOCO智能Mesh三键开关|24948|
|nbxh.switch.sw3b01|JOCO智能Mesh三键屏显开关|25470|
|nbxh.switch.xhlhv1|JOCO磁保持零火开关（Mesh2.0 单路）|39834|
|nbxh.switch.xhlhv2|JOCO磁保持零火开关（Mesh2.0 双路）|39835|
|nbxh.switch.xhlhv3|JOCO磁保持零火开关（Mesh2.0 三路）|39836|
|nbxh.switch.xhlhv4|JOCO磁保持零火开关（Mesh2.0 四路）|39837|
|nowoo.switch.s11k|乐蜗一键智能开关S1|30370|
|nowoo.switch.s12k|乐蜗二键智能开关S1|30371|
|nowoo.switch.s13k|乐蜗三键智能开关S1|30372|
|nvcsmt.switch.bis101|小雷易家鸿雪Plus一键屏显开关|37212|
|nvcsmt.switch.bis201|小雷易家鸿雪Plus二键屏显开关|37213|
|nvcsmt.switch.bis302|小雷易家云雪系列四寸屏显开关|36885|
|nvcsmt.switch.bis303|小雷易家鸿雪Plus三键屏显开关|37214|
|nvcsmt.switch.bis402|小雷易家云雪系列四键屏显开关|36886|
|nvcsmt.switch.bis403|小雷易家鸿雪Plus四键屏显开关|37215|
|nvcsmt.switch.bis404|小雷易家暮雪Lite四寸屏显开关|37216|
|ocy.switch.bln41|OCY智能一键开关MESH2.0|34652|
|ocy.switch.bln42|OCY智能二键开关MESH2.0|34653|
|ocy.switch.bln43|OCY智能三键开关MESH2.0|34654|
|ocy.switch.bln44|OCY智能四键开关MESH2.0|34655|
|ocy.switch.bln46|OCY智能六键开关MESH2.0|34656|
|ogl.switch.sw1a01|欧格朗智能一键开关|37406|
|ogl.switch.sw2a01|欧格朗智能二键开关|37407|
|ogl.switch.sw3a01|欧格朗智能三键开关|37408|
|ogl.switch.sw4a01|欧格朗智能四键开关|37409|
|oit.plug.cb2|欧伦特智能插座CB2|17965|
|oit.plug.cb3|欧伦特智能插座CB3|16197|
|oit.plug.cb6|欧伦特智能插座CB6|21595|
|oit.plug.cb7|欧伦特智能排插CB7|23795|
|okdz.switch.sw4a01|OKOK四路屏显智能开关|34309|
|oml.remote.omxn4|欧曼无线旋钮遥控开关|38512|
|oml.remote.sw1b01|欧曼智能无线旋钮遥控开关|35618|
|oml.switch.sw1a01|OML一键智能复合面板|31183|
|oml.switch.sw1c01|欧曼智能复合开关K8（一键）|34948|
|oml.switch.sw2a01|OML二键智能复合面板|31184|
|oml.switch.sw2c01|欧曼智能复合开关K8（二键）|34949|
|oml.switch.sw3a01|OML三键智能复合面板|31185|
|oml.switch.sw3c01|欧曼智能复合开关K8（三键）|34950|
|oml.switch.sw4a01|OML四键智能复合面板|31187|
|oml.switch.sw4d01|欧曼智能屏显开关K8 Pro（四键）|35319|
|oml.switch.sxpx01|欧曼智能屏显开关MK90(一键)|36537|
|oml.switch.sxpx02|欧曼智能屏显开关MK90(二键)|36538|
|oml.switch.sxpx03|欧曼智能屏显开关MK90(三键)|36539|
|oppein.switch.sw1a01|海烈鸟-智能零火一键开关|39056|
|oppein.switch.sw2a01|海烈鸟-智能零火二键开关|39057|
|oppein.switch.sw3a01|海烈鸟-智能零火三键开关|39058|
|opple.plug.001019|OPPLE 智能五孔插座|82765|
|opple.remote.02001c|OPPLE 六键磁吸场景开关|82764|
|opple.remote.5pb111|欧普无线开关（单键）|6047|
|opple.remote.5pb112|欧普无线开关（双键）|6048|
|opple.remote.5pb113|欧普无线开关（三键）|6049|
|opple.switch.00101a|OPPLE 三位智能开关 高清屏|82760|
|opple.switch.00101c|OPPLE 六位智能开关 高清屏|83097|
|opple.switch.00101e|OPPLE 墙面旋钮|82762|
|opple.switch.0010d3|OPPLE 三位智能开关|82753|
|opple.switch.0010d5|OPPLE 一位智能开关|82732|
|opple.switch.0010d6|OPPLE 二位智能开关|82752|
|opple.switch.0010d7|OPPLE 六位智能开关|83096|
|opple.switch.lbs01a|欧普单火蓝牙开关MESH(单键)|6042|
|opple.switch.lbs02a|欧普单火蓝牙开关MESH(双键)|6043|
|opple.switch.lbs03a|欧普单火蓝牙开关MESH(三键)|6044|
|osteen.switch.lnpx4k|OSTEEN智能彩屏开关（四键）|40138|
|osteen.switch.sw1a01|OSTEEN智能开关（单键Mesh版）|28178|
|osteen.switch.sw2a01|OSTEEN智能开关（双键Mesh版）|28179|
|osteen.switch.sw3a01|OSTEEN智能开关（三键Mesh版）|28180|
|osteen.switch.sw4a01|OSTEEN智能开关（四键Mesh版）|28181|
|osteen.switch.sw4a05|OSTEEN智能屏显开关（四键）|38852|
|ouxim.switch.lxkg4|OUXIM圆屏四键开关|35483|
|ouxim.switch.oxmkg1|OUXIM智能一键开关|30121|
|ouxim.switch.oxmkg2|OUXIM智能二键开关|30122|
|ouxim.switch.oxmkg3|OUXIM智能三键开关|30123|
|ouxim.switch.oxmkg4|OUXIM智能四键开关|30124|
|ouxim.switch.px1|OUXIM智能一键屏显开关|30492|
|ouxim.switch.px2|OUXIM智能二键屏显开关|30493|
|ouxim.switch.px3|OUXIM智能三键屏显开关|30494|
|ouxim.switch.sw1a02|OUXIM一键智能开关Ultra|29855|
|ouxim.switch.sw2a02|OUXIM二键智能开关Ultra|29856|
|ouxim.switch.sw3a02|OUXIM三键智能开关Ultra|29857|
|ouxim.switch.sw4a02|OUXIM四键智能开关Ultra|29858|
|ouxim.switch.sw4a03|OUXIM四键屏显开关Ultra|30284|
|ouxim.switch.sw8a01|OUXIM八键智能开关Ultra|39772|
|pak.remote.ts1|三雄极光Pak 臻享无线遥控开关|26477|
|pak.switch.sw1a01|三雄极光Pak 智能开关一位|21985|
|pak.switch.sw1b01|三雄极光Pak 智能开关 智享Pro一位|25557|
|pak.switch.sw1c01|三雄极光Pak 智能开关 一位 2.0|31595|
|pak.switch.sw2a01|三雄极光Pak 智能开关二位|21986|
|pak.switch.sw2b01|三雄极光Pak 智能开关 智享Pro二位|25558|
|pak.switch.sw2c01|三雄极光Pak 智能开关 二位 2.0|31596|
|pak.switch.sw3a01|三雄极光Pak 智能开关三位|21987|
|pak.switch.sw3b01|三雄极光Pak 智能开关 智享Pro三位|25559|
|pak.switch.sw3c01|三雄极光Pak 臻享 智能触屏开关|31232|
|pak.switch.sw3c02|三雄极光Pak 智能开关 三位 2.0|31597|
|pak.switch.sw3c03|三雄极光Pak 智能开关 三开+三场景 2.0|31599|
|pak.switch.sw4a01|三雄极光Pak 智能开关四位|21988|
|pak.switch.sw4b01|三雄极光Pak 智能开关 智享Pro三位+场景|25560|
|pak.switch.sw4c01|三雄极光Pak 智能开关 四位 2.0|31598|
|pak.switch.sw6a02|三雄极光Pak 智能开关三位+三场景|22898|
|pbm.switch.sw1a01|柏曼智能单键墙壁开关|31573|
|pbm.switch.sw2a02|柏曼智能双键墙壁开关|31574|
|pbm.switch.sw3a02|柏曼智能三键墙壁开关|31575|
|point.switch.a9max1|现代点一位智能开关（灵动岛）|38872|
|point.switch.a9max2|现代点二位智能开关（灵动岛）|38873|
|point.switch.a9max3|现代点三位智能开关（灵动岛）|38874|
|point.switch.a9max4|现代点四位智能开关（灵动岛）|38875|
|point.switch.fn01|现代点一位智能开关蜂鸟5.0|33802|
|point.switch.fn02|现代点二位智能开关蜂鸟5.0|33803|
|point.switch.fn03|现代点三位智能开关蜂鸟5.0|33804|
|point.switch.fn04|现代点四位智能开关蜂鸟5.0|33805|
|point.switch.mpx01|现代点一键屏显开关M5-K1|36385|
|point.switch.mpx02|现代点二键屏显开关M5-K2|36386|
|point.switch.mpx03|现代点三键屏显开关M5-K3|36387|
|point.switch.sw1b01|现代点A8易点一位智能开关|36542|
|point.switch.sw1c01|现代点S8云界智能一键开关|40459|
|point.switch.sw2b01|现代点A8易点二位智能开关|36543|
|point.switch.sw2c01|现代点S8云界智能二键开关|40460|
|point.switch.sw3b01|现代点A8易点三位智能开关|36544|
|point.switch.sw3c01|现代点S8云界智能三键开关|40461|
|point.switch.sw4b01|现代点A8易点四位智能开关|36545|
|point.switch.sw4c01|现代点S8云界智能四键开关|40462|
|poyde.switch.bjtdq5|博义德智能通断器WiFi版|31848|
|poyde.switch.tdq3|博义德智能通断器Mesh版|31842|
|ppe.cs.swk01|MAIHUI智能插卡取电器2.0|30683|
|ppe.plug.znwk01|MAIHUI智能Mesh插座|37935|
|ppe.switch.bdh1|MAIHUI一开智能开关2.0|32010|
|ppe.switch.bdh2|MAIHUI二开智能开关2.0|32011|
|ppe.switch.bdh3|MAIHUI三开智能开关2.0|32012|
|ppe.switch.bdh4|MAIHUI四开智能开关2.0|32013|
|ppe.switch.bln31|XWWL一开屏显开关|27667|
|ppe.switch.bln32|XWWL二开屏显开关|27669|
|ppe.switch.bln33|XWWL三开屏显开关|27670|
|ppe.switch.pxln4|XWWL四开屏显开关|24389|
|ppe.switch.sw1a01|MAIHUI 一开智能开关2.0|30053|
|ppe.switch.sw1c01|MAIHUI A15智能开关一键|38808|
|ppe.switch.sw2a01|MAIHUI 二开智能开关2.0|30054|
|ppe.switch.sw2c01|MAIHUI A15智能开关二键|38809|
|ppe.switch.sw3a01|MAIHUI 三开智能开关2.0|30055|
|ppe.switch.sw3c01|MAIHUI A15智能开关三键|38810|
|ppe.switch.sw4a01|MAIHUI 四开智能开关2.0|30056|
|ppe.switch.sw4c01|MAIHUI A15智能开关四键|38811|
|ptx.switch.f1gq4|平头熊高清屏显开关 四键（F1）|36009|
|ptx.switch.f1sw1|平头熊高清屏显开关 单键（F1）|37430|
|ptx.switch.f1sw2|平头熊高清屏显开关 双键（F1）|37432|
|ptx.switch.f1sw3|平头熊高清屏显开关 三键（F1）|37433|
|ptx.switch.f2tp69|平头熊6.9寸高清屏幕开关 (F2)|37587|
|ptx.switch.fggq4|平头熊高清屏显开关 四键（梵高）|34431|
|ptx.switch.fgsw1|平头熊高清屏显开关 单键（梵高）|36550|
|ptx.switch.fgsw2|平头熊高清屏显开关 双键（梵高）|36551|
|ptx.switch.fgsw3|平头熊高清屏显开关 三键（梵高）|36552|
|ptx.switch.ptxf13|平头熊超薄高清屏幕开关|33940|
|ptx.switch.ptxfx1|平头熊 F2智能开关 单键|36247|
|ptx.switch.ptxfx2|平头熊 F2智能开关 双键|36248|
|ptx.switch.ptxfx3|平头熊 F2智能开关 三键|36249|
|ptx.switch.ptxfx4|平头熊 F2智能开关 四键|36250|
|ptx.switch.x6pro1|平头熊 X6 Pro智能开关 单键|36602|
|ptx.switch.x6pro2|平头熊 X6 Pro智能开关 双键|36603|
|ptx.switch.x6pro3|平头熊 X6 Pro智能开关 三键|36604|
|ptx.switch.x6pro4|平头熊 X6 Pro智能开关 四键|36605|
|pwzn.plug.banana|智能无线墙充|70445|
|pwzn.relay.apple|16路继电器|66805|
|pwzn.relay.banana|16路控制器Modbus版|67227|
|pzg.plug.0002|LKRQ电脑开机卡（Mesh2.0）|25505|
|pzg.plug.1127|LKRQ电脑开机卡|24750|
|qbx.remote.sw7a01|墙壁侠M4智能旋钮无线开关|18744|
|qbx.switch.sw1b02|墙壁侠一位智能开关|39885|
|qbx.switch.sw2b02|墙壁侠二位智能开关|39886|
|qbx.switch.sw3b02|墙壁侠三位智能开关|39887|
|qbx.switch.sw4b02|墙壁侠四位智能开关|39888|
|qimi.switch.sw1b01|邮科通信一键智能开关|21572|
|qimi.switch.sw2b01|邮科通信二键智能开关|21576|
|qimi.switch.sw3b01|邮科通信三键智能开关|21577|
|qimi.switch.sw4b01|邮科通信四键智能开关|21578|
|qjiang.plug.v1|QM智能Mesh插座|22134|
|qjiang.plug.v2|QM智能WiFi插座|24642|
|qjiang.switch.11ssw1|QM智能Mesh开关U系列（单键）|20396|
|qjiang.switch.11ssw2|QM智能Mesh开关U系列（双键）|20395|
|qjiang.switch.11ssw3|QM智能Mesh开关U系列（三键）|20394|
|qjiang.switch.12gsw1|QM智能Mesh开关G系列（单键）|21345|
|qjiang.switch.12gsw2|QM智能Mesh开关G系列（双键）|21344|
|qjiang.switch.12gsw3|QM智能Mesh开关G系列（三键）|21343|
|qjiang.switch.12gsw4|QM智能Mesh开关G系列（四键）|21342|
|qjiang.switch.12qj01|QM智能Mesh情景开关Q系列（一位复合开关）|20940|
|qjiang.switch.12qj02|QM智能Mesh情景开关Q系列（二位复合开关）|20941|
|qjiang.switch.12qj03|QM智能Mesh情景开关Q系列（三位复合开关）|20942|
|qjiang.switch.12qj04|QM智能Mesh情景开关Q系列（四位复合开关）|20943|
|qjiang.switch.12ssw1|QM智能Mesh开关S系列（单键）|20693|
|qjiang.switch.12ssw2|QM智能Mesh开关S系列（双键）|20694|
|qjiang.switch.12ssw3|QM智能Mesh开关S系列（三键）|20695|
|qjiang.switch.12ssw4|QM智能Mesh开关S系列（四键）|20696|
|qjiang.switch.b12sw1|QM智能Mesh开关P系列（单键）|18246|
|qjiang.switch.b12sw2|QM智能Mesh开关P系列（双键）|18245|
|qjiang.switch.b12sw3|QM智能Mesh开关P系列（三键）|18244|
|qjiang.switch.b12sw4|QM智能Mesh开关P系列（四键）|18243|
|qjiang.switch.fire1|QM单火开关（单键）|13640|
|qjiang.switch.fire11|QM智能开关（单键）|17606|
|qjiang.switch.fire2|QM单火开关（双键）|13638|
|qjiang.switch.fire3|QM单火开关（三键）|13378|
|qjiang.switch.fire33|QM智能开关（三键）|17604|
|qjiang.switch.firey2|QM智能开关（双键）|17605|
|qjiang.switch.firey4|QM智能开关（四键）|17809|
|qjiang.switch.oled01|GS一位零火屏显智能开关|21219|
|qjiang.switch.oled03|GS三位零火屏显智能开关|21216|
|qjiang.switch.oled04|GS四位零火屏显智能开关|21215|
|qjiang.switch.oled22|GS二位零火屏显智能开关|21218|
|qjiang.switch.zero11|QM智能开关（单键）|15638|
|qjiang.switch.zero22|QM智能开关（双键）|15637|
|qjiang.switch.zero33|QM智能开关（三键）|15635|
|qjiang.switch.zero44|QM智能开关（四键）|17579|
|qmi.plug.psv1|爱国者智能插排|71173|
|qmi.plug.psv3|小米智能插线板2 5位插孔版|4896|
|qmi.powerstrip.v1|青米智能插排|121|
|qtzm.switch.qtkg1|秋田智能开关（一位）|31139|
|qtzm.switch.qtkg2|秋田智能开关（两位）|31140|
|qtzm.switch.qtkg3|秋田智能开关（三位）|31141|
|qtzm.switch.qtkg4|秋田智能开关（四位）|31142|
|qzgd.switch.sw1a02|擎洲一键智能开关|18338|
|qzgd.switch.sw2a02|擎洲二键智能开关|18361|
|qzgd.switch.sw3a02|擎洲三键智能开关|18362|
|qzgd.switch.sw4a01|擎洲四键智能开关|17223|
|qzgd.switch.sw4a02|擎洲八键智能开关|17224|
|rhj.switch.l821|乐天派智能开关Lite（单开 零火版）|23070|
|rhj.switch.l821b|乐天派智能开关Lite（双开 零火版）|23256|
|rhj.switch.l821c|乐天派智能开关Lite（三开 零火版）|23257|
|rinmin.switch.sjdkg1|菱敏智能单键开关|33776|
|rinmin.switch.sjdkg2|菱敏智能双键开关|33777|
|rinmin.switch.sjdkg3|菱敏智能三键开关|33778|
|rinmin.switch.sjdkg4|菱敏智能四键开关|33779|
|riot.plug.003|小锐wifi智能插座-基础版|15818|
|riot.plug.006|希小智插座精灵|16329|
|riot.switch.001|小R智能双控开关|12187|
|riot.switch.11|辰域智能电表|16447|
|rjkj.switch.b103|数字断路器|3379|
|rjkj.switch.mj152|睿据交流单相数字断路器2型|13578|
|rjxn20.plug.rjcz|RJ智能蓝牙插座|12531|
|rjxn20.switch.rixmek|RJ智能二键开关Mesh版|12096|
|rjxn20.switch.rixmlk|RJ智能四键开关Mesh版|12098|
|rjxn20.switch.rixmsk|RJ智能三键开关Mesh版|12097|
|rjxn20.switch.rixmyk|RJ智能一键开关Mesh版|12095|
|rjxn20.switch.rjkg1|RJ一路智能开关（Mesh2.0）|31120|
|rjxn20.switch.rjkg2|RJ二路智能开关（Mesh2.0）|31121|
|rjxn20.switch.rjkg3|RJ三路智能开关（Mesh2.0）|31122|
|rjxn20.switch.rjkg4|RJ四路智能开关（Mesh2.0）|31123|
|rjxn20.switch.rjtdm|RJ智能蓝牙通断器|12592|
|rtzn.switch.sw1a01|睿态智能开关Mesh2.0（一键）|29416|
|rtzn.switch.sw2a01|睿态智能开关Mesh2.0（二键）|29417|
|rtzn.switch.sw3a01|睿态智能开关Mesh2.0（三键）|29418|
|rtzn.switch.sw4a01|睿态智能开关Mesh2.0（四键）|29419|
|runhu.plug.pw5u1|岚威五路分控智能排插|31440|
|rusee.switch.sw4a02|如见智能屏显开关M|33415|
|sagewe.plug.001|Sagewe智能插座Xs11-M|24602|
|sagewe.plug.002|Sagewe智能排插M1scu311-GB15W-M|24706|
|sagewe.plug.003|Sagewe智能排插M1scu311-GB35W-M|24707|
|sagewe.plug.005|Sagewe智能插座F2501-GB-M|27677|
|sagewe.plug.006|Sagewe四位智能排线板M4s411-GB-M|27698|
|san.switch.sw1a01|晟科瑞情景智能灯控开关V1|25372|
|san.switch.sw2a01|晟科瑞情景智能灯控开关V2|25373|
|san.switch.sw3a01|晟科瑞情景智能灯控开关V3|25374|
|san.switch.sw4a01|晟科瑞情景智能灯控开关V4|25375|
|sayso.switch.sw1a01|SAYSO智能开关（一键）|15159|
|sayso.switch.sw2a01|SAYSO智能开关（二键）|15160|
|sayso.switch.sw3a01|SAYSO智能开关（三键）|15161|
|sayso.switch.sw4a01|SAYSO智能开关（四键）|15162|
|sayso.switch.sw4b01|商颂超薄智能屏显开关四开2.0|27926|
|scc.remote.ru02|Simon二位随意贴开关（电池版）|17538|
|scc.remote.ru06|Simon四位随意贴开关（电池版）|17584|
|scc.switch.bl01|Simon智能开关（一位 单零火版）|17499|
|scc.switch.bl02|Simon智能开关（二位 单零火版）|17500|
|scc.switch.bl03|Simon智能开关（三位 单零火版）|17501|
|scc.switch.bln01|Simon智能开关（一位 零火版）|17661|
|scc.switch.bln02|Simon智能开关（二位 零火版）|17662|
|scc.switch.bln03|Simon智能开关（三位 零火版）|17663|
|scc.switch.bln21|Simon智能一键开关|25213|
|scc.switch.bln22|Simon智能二键开关|25214|
|scc.switch.bln23|Simon智能三键开关|25215|
|scc.switch.bln24|Simon智能四键开关|25216|
|scc.switch.bln41|Simon智能开关（一开 零火版）|29131|
|scc.switch.bln42|Simon智能开关（二开 零火版）|29132|
|scc.switch.bln43|Simon智能开关（三开 零火版）|29133|
|scc.switch.blnx4|Simon智能开关（四开 零火版)|32118|
|scc.switch.sup3|Simon智能超级屏控开关|28910|
|scc.switch.sw04|Simon智能屏键开关|31713|
|scdvb.switch.sw3|SoChuang智能开关Ultra(三键)|25861|
|seity.switch.sw1a01|西铁照明智能一键开关mesh|30170|
|seity.switch.sw2a01|西铁照明智能二键开关mesh|30256|
|seity.switch.sw3a01|西铁照明智能三键开关mesh|30257|
|seity.switch.sw4a01|西铁照明智能四键开关mesh|30258|
|seity.switch.sw4b01|西铁照明四键屏显开关Ultra|31101|
|seomsh.switch.sw1a01|星月影Home Hi智能开关（一键）|24383|
|seomsh.switch.sw2a01|星月影Home Hi智能开关（二键）|24384|
|seomsh.switch.sw3a01|星月影Home Hi智能开关（三键）|24385|
|seomsh.switch.sw4a01|星月影Home Hi智能开关（四键）|24386|
|sfl.switch.fsls01|FSL 屏显零火一开|40616|
|sfl.switch.fsls02|FSL 屏显零火二开|40617|
|sfl.switch.fsls03|FSL 屏显零火三开|40618|
|sfl.switch.fsls04|FSL 屏显零火四开|40619|
|sfl.switch.sw1a01|FSL一位智能开关|35460|
|sfl.switch.sw1b01|FSL 一位零火开关BLE|39405|
|sfl.switch.sw2a01|FSL二位智能开关|35461|
|sfl.switch.sw2b01|FSL 二位零火开关BLE|39406|
|sfl.switch.sw3a01|FSL三位智能开关|35462|
|sfl.switch.sw3a03|FSL 四寸智能彩屏开关|39287|
|sfl.switch.sw3b01|FSL 三位零火开关BLE|39407|
|sfl.switch.sw4a01|FSL四位智能开关|35463|
|sfl.switch.sw4b01|FSL 四位零火开关BLE|39410|
|sfy.remote.ws001|索菲亚智能无线开关M1|28362|
|sfy.switch.css002|索菲亚智慧屏开关M1|31783|
|sfy.switch.dc001|索菲亚智能柜通断器M1|33707|
|sfy.switch.sw001|索菲亚智能零火开关一键M1|23561|
|sfy.switch.sw002|索菲亚智能零火开关二键M1|23625|
|sfy.switch.sw003|索菲亚智能零火开关三键M1|23626|
|sfy.switch.sw004|索菲亚智能零火开关四键M1|23627|
|sfy.switch.sw101|索菲亚智能单火开关一键M1|27291|
|sfy.switch.sw102|索菲亚智能单火开关二键M1|27292|
|sfy.switch.sw103|索菲亚智能单火开关三键M1|27293|
|sh1966.switch.sw1a01|Share蓝牙Mesh2.0超薄 单键开关|27447|
|sh1966.switch.sw1b01|Share蓝牙Mesh2.0超薄AG玻璃 单键开关|27643|
|sh1966.switch.sw2a01|Share蓝牙Mesh2.0超薄 二键开关|27448|
|sh1966.switch.sw2b01|Share蓝牙Mesh2.0超薄AG玻璃 二键开关|27644|
|sh1966.switch.sw3a01|Share蓝牙Mesh2.0超薄 三键开关|27449|
|sh1966.switch.sw3b01|Share蓝牙Mesh2.0超薄AG玻璃 三键开关|27645|
|sh1966.switch.sw4b01|Share蓝牙Mesh2.0超薄AG玻璃 四键带屏开关|27646|
|sh1966.switch.sw4c02|Share蓝牙Mesh2.0超薄 四键开关|33384|
|shadow.switch.sw0a01|迅透光感天幕控制开关|19917|
|sharge.plug.sj01|闪极  100W 迷你充电器（蓝牙版）|7708|
|shhf.plug.c001|智慧计量插座WiFi版|18106|
|shhf.plug.spwc02|智慧插座WiFi版|14336|
|shhf.switch.splgs1|智能通断器BLE Mesh版|10132|
|shibei.switch.sw1a01|视贝智家开关2.0（一开）|31104|
|shibei.switch.sw2a01|视贝智家开关2.0（二开）|31105|
|shibei.switch.sw3a01|视贝智家开关2.0（三开）|31106|
|shibei.switch.sw4|视贝智家屏显开关2.0（四开）|32139|
|shibei.switch.sw4a01|视贝智家开关2.0（四开）|31107|
|shidun.switch.sw1a01|SHIDUN-Q4L智能一位零火开关|30859|
|shidun.switch.sw2a01|SHIDUN-Q4L智能二位零火开关|30860|
|shidun.switch.sw3a01|SHIDUN-Q4L智能三位零火开关|30861|
|shidun.switch.sw4a01|SHIDUN-Q4L智能四位零火开关|30862|
|shuse.plug.ifrc1|树色手指机器人伴侣（Mesh）|21689|
|shuse.plug.sstdqm|树色通断器（Mesh2.0）|29232|
|shuse.plug.v7icm|树色智能控制器Mesh|26225|
|shuse.plug.v7icw|树色智能控制器Wifi|26224|
|shuse.plug.v8icm|树色智能控制器计量版Mesh|26223|
|shuse.plug.v8icwf|树色智能控制器计量版Wifi|26414|
|shuse.remote.v6swx1|树色无线开关一键（BLE）|36399|
|shuse.remote.v6swx3|树色无线开关三键（BLE）|36397|
|shuse.remote.v6wx2|树色无线开关二键（BLE）|36633|
|shuse.remote.yk20|树色小圆豆无线开关（BLE）|36214|
|shuse.switch.sskg1|树色智能一键开关(Mesh2.0)|31129|
|shuse.switch.sskg22|树色智能二键开关(Mesh2.0)|32195|
|shuse.switch.sskg3|树色智能三键开关(Mesh2.0)|31131|
|shuse.switch.sskg4|树色智能四键开关(Mesh2.0)|31133|
|shuse.switch.sskg6|树色四路通断器 (Mesh2.0)|33477|
|shuse.switch.v9s24|树色通断器（WiFi）|35523|
|sie.remote.v52kwm|SIECARE 智能场景开关|26221|
|siemen.remote.arinap|西门子荟辰&荟绎智能一位随意贴|18208|
|siemen.remote.asw002|西门子荟辰&荟绎智能二位随意贴|19495|
|siemen.switch.5ta771|西门子智能一位开关|38730|
|siemen.switch.5ta772|西门子智能二位开关|38735|
|siemen.switch.5ta773|西门子智能三位开关|38736|
|siemen.switch.5ta774|西门子智能四位开关|38737|
|siemen.switch.arina1|西门子荟辰&荟绎智能一位单火开关|14739|
|siemen.switch.arina2|西门子荟辰&荟绎智能二位单火开关|14740|
|siemen.switch.arina3|西门子荟辰&荟绎智能三位单火开关|14741|
|signfy.switch.bm0yz1|飞利浦智能开关_MifyPL30_1K|34140|
|signfy.switch.bm0yz2|飞利浦智能开关_MifyPL30_2K|34141|
|signfy.switch.bm0yz3|飞利浦智能开关_MifyPL30_3K|34142|
|signfy.switch.bm0yz4|飞利浦智能开关_MifyPL30_4K|34143|
|sixwgh.plug.v7icm|文光汇智能插座（Mesh）|26430|
|sixwgh.plug.v7icw1|文光汇智能插座（WiFi）|26434|
|sixwgh.plug.v8icm1|文光汇智能插座（Mesh计电量）|26435|
|sixwgh.plug.v8icwf|文光汇智能插座（WiFi计电量）|26428|
|sixwgh.plug.v9wh|文光汇智能插座（Wi-Fi）|31908|
|sixwgh.plug.whzncz|文光汇智能插座Mesh|37831|
|sixwgh.switch.whtdq2|文光汇智能通断器（Mesh）|38755|
|slf.cs.ckd5|智拉斐智能插卡取电开关（D8）|11669|
|slf.plug.sw0a01|智拉斐智能二三极插座（D8）|7307|
|slf.remote.lh4d5|智拉斐四键零火场景开关（D5）|10319|
|slf.remote.lh6d5|智拉斐六键零火场景开关（D5）|10320|
|slf.remote.rem01|智拉斐单键零火场景开关（Y8）|8532|
|slf.remote.rem02|智拉斐双键零火场景开关（Y8）|8850|
|slf.remote.rem03|智拉斐三键零火场景开关（Y8）|8851|
|slf.remote.rem04|智拉斐四键零火场景开关（HR7）|8559|
|slf.remote.rem05|智拉斐六键零火场景开关（Y8）|9335|
|slf.remote.rem06|智拉斐四键零火场景开关（Y8）|9497|
|slf.remote.sen01|智拉斐智能紧急呼叫开关（HR7）|8628|
|slf.remote.sen02|智拉斐智能紧急呼叫开关（D8）|9336|
|slf.switch.bin31|拉斐智能一键开关|28467|
|slf.switch.bin32|拉斐智能二键开关|28468|
|slf.switch.bin33|拉斐智能三键开关|28469|
|slf.switch.bin34|拉斐智能四键开关|28470|
|slf.switch.bin6|拉斐智能六键开关|28471|
|slf.switch.lh1d5|智拉斐单键零火灯控开关（D5）|10109|
|slf.switch.lh2d5|智拉斐双键零火灯控开关（D5）|10010|
|slf.switch.lh3d5|智拉斐三键零火灯控开关（D5）|10108|
|slf.switch.lh4d5|智拉斐四键零火灯控开关（D5）|10011|
|slf.switch.sw1a01|智拉斐单键零火灯控开关（Y8）|7266|
|slf.switch.sw1b01|智拉斐单键零火灯控开关（HR7）|8739|
|slf.switch.sw2a01|智拉斐双键零火灯控开关（Y8）|7267|
|slf.switch.sw2b01|智拉斐双键零火灯控开关（HR7）|8740|
|slf.switch.sw3a01|智拉斐三键零火灯控开关（Y8）|7268|
|slf.switch.sw3b01|智拉斐三键零火灯控开关（HR7）|8741|
|slf.switch.sw4a01|智拉斐四键零火灯控开关（Y8）|7311|
|slf.switch.sw4b01|智拉斐四键零火灯控开关（HR7）|8742|
|slf.switch.zlfx1|智拉斐一键屏显超薄开关X-H5A|31931|
|slf.switch.zlfx2|智拉斐二键屏显超薄开关X-H5A|28520|
|slf.switch.zlfx3|智拉斐三键屏显超薄开关X-H5A|31932|
|slf.switch.zlfx4|智拉斐四键屏显超薄开关X-H5A|28521|
|slf.switch.zlfx6|智拉斐六键屏显超薄开关X-H5A|31933|
|smartj.plug.sjsc86|SmartJoy智能墙壁插座（WiFi版）|68513|
|smartj.switch.sjlh01|SmartJoy智简墙壁开关（零火单键WiFi版）|68509|
|smartj.switch.sjlh02|SmartJoy智简墙壁开关（零火双键WiFi版）|68510|
|smartj.switch.sjlh03|SmartJoy智简墙壁开关（零火三键WiFi版）|68511|
|smartj.switch.sjlh1e|SmartJoy智享墙壁开关（零火单键WiFi版）|70663|
|smartj.switch.sjlh1p|SmartJoy极智墙壁开关（零火单键蓝牙Mesh版）|18196|
|smartj.switch.sjlh1s|SmartJoy智臻墙壁开关（零火单键蓝牙Mesh版）|3763|
|smartj.switch.sjlh2e|SmartJoy智享墙壁开关（零火双键WiFi版）|70664|
|smartj.switch.sjlh2p|SmartJoy极智墙壁开关（零火双键蓝牙Mesh版）|18197|
|smartj.switch.sjlh2s|SmartJoy智臻墙壁开关（零火双键蓝牙Mesh版）|3764|
|smartj.switch.sjlh3e|SmartJoy智享墙壁开关（零火三键WiFi版）|70665|
|smartj.switch.sjlh3p|SmartJoy极智墙壁开关（零火三键蓝牙Mesh版）|18198|
|smartj.switch.sjlh3s|SmartJoy智臻墙壁开关（零火三键蓝牙Mesh版）|3765|
|smartj.switch.sjlh4p|SmartJoy极智墙壁开关（零火四键蓝牙Mesh版）|18199|
|smartj.switch.sjlh4s|SmartJoy智臻墙壁开关（零火四键蓝牙Mesh版）|8198|
|smartj.switch.sjlh8p|SmartJoy极智墙壁开关（八键情景蓝牙Mesh版）|18201|
|soron.switch.sw0a01|知简智能迷你通断器|39311|
|soron.switch.sw1a01|知简智能开关 一位|28563|
|soron.switch.sw2a01|知简智能开关 二位|28564|
|soron.switch.sw3a01|知简智能开关 三位|28565|
|soron.switch.sw4a01|知简智能开关 四位|37281|
|soron.switch.sw8a03|知简智能开关 八键|40859|
|ssdg.switch.sw1a01|深思一位智能开关|30679|
|ssdg.switch.sw2a01|深思二位智能开关|30755|
|ssdg.switch.sw3a01|深思三位智能开关|30756|
|ssdg.switch.sw4a01|深思四位智能开关|30757|
|ssznkj.switch.sw1a01|松鼠一开智能开关|30436|
|ssznkj.switch.sw2a01|松鼠二开智能开关|30437|
|ssznkj.switch.sw3a01|松鼠三开智能开关|30438|
|ssznkj.switch.sw3b01|松鼠三开智能屏显开关|30698|
|ssznkj.switch.sw4a01|松鼠四开智能屏显开关|30441|
|ssznkj.switch.sw4a02|松鼠四开智能开关|31566|
|star1.switch.sw1|星发现智能开关(一位)|27030|
|star1.switch.sw2|星发现智能开关(二位)|30874|
|star1.switch.sw3|星发现智能开关(三位)|27029|
|star1.switch.sw4|星发现智能开关(四位)|30872|
|suis.controller.pad01|菲马仕控制面板|72496|
|symi.cs.ck01|亖米智能插卡取电器|25438|
|symi.remote.ts1|亖米六键无线开关|11950|
|symi.switch.apple|亖米16路控制器|14644|
|symi.switch.bln31|亖米一键智能开关|25425|
|symi.switch.bln32|亖米二键智能开关|25426|
|symi.switch.bln33|亖米三键智能开关|25427|
|symi.switch.bln34|亖米四键智能开关|25428|
|symi.switch.bln36|亖米六键智能开关|25435|
|symi.switch.bln38|亖米八键智能开关|25436|
|symi.switch.s01|亖米多功能开关mesh版|20798|
|symi.switch.sw1a01|亖米一键开关mesh版|10050|
|symi.switch.sw1c01|晓翼一键开关mesh版|15711|
|symi.switch.sw1d02|亖米Mesh一键开关Ultra|21364|
|symi.switch.sw1e02|晓翼Mesh一键开关Ultra|21653|
|symi.switch.sw2a01|亖米二键开关mesh版|10051|
|symi.switch.sw2c01|晓翼二键开关mesh版|15712|
|symi.switch.sw2d01|亖米智慧屏开关|16532|
|symi.switch.sw2d02|亖米Mesh二键开关Ultra|21365|
|symi.switch.sw2e02|晓翼Mesh二键开关Ultra|21654|
|symi.switch.sw3a01|亖米三键开关mesh版|10052|
|symi.switch.sw3c01|晓翼三键开关mesh版|15713|
|symi.switch.sw3d02|亖米Mesh三键开关Ultra|21366|
|symi.switch.sw3e02|晓翼Mesh三键开关Ultra|21655|
|symi.switch.sw4a01|亖米四键开关mesh版|10053|
|symi.switch.sw4c01|晓翼四键开关mesh版|15714|
|symi.switch.sw4d02|亖米Mesh四键开关Ultra|21367|
|symi.switch.sw4e02|晓翼Mesh四键开关Ultra|21656|
|symi.switch.sw6a01|亖米六键开关mesh版|11949|
|symi.switch.sw8a01|亖米八键开关mesh版|10054|
|symi.switch.z501|亖米Z5一键屏显开关|38426|
|symi.switch.z502|亖米Z5二键屏显开关|38427|
|symi.switch.z503|亖米Z5三键屏显开关|38428|
|symi.switch.z7002|亖米-Z7二键智能开关|31439|
|symi.switch.z703|亖米-Z7三键智能开关|31427|
|symi.switch.z704|亖米-Z7四键智能开关|31428|
|symi.switch.z706|亖米-Z7六键智能开关|31429|
|syniot.switch.s1|智能开关一位|68853|
|syniot.switch.s2|智能开关二位|68914|
|syniot.switch.s3|智能开关三位|68927|
|syniot.switch.t1|居意智能开关一位|69244|
|syniot.switch.t2|居意智能开关二位|69245|
|syniot.switch.t3|居意智能开关三位|69246|
|szdbf.switch.sw1a01|定不凡 mesh2.0 智能开关 单键|28349|
|szdbf.switch.sw2a01|定不凡 mesh2.0 智能开关 双键|28350|
|szdbf.switch.sw3a01|定不凡 mesh2.0 智能开关 三键|28351|
|szdbf.switch.sw4a01|定不凡 mesh2.0 智能开关 四键|28352|
|taili.switch.px01|泰力ST8屏显一键开关|35285|
|taili.switch.px02|泰力ST8屏显二键开关|35286|
|taili.switch.px03|泰力ST8屏显三键开关|35287|
|taili.switch.sw1a01|泰力ST7系列零火智能开关一开|31645|
|taili.switch.sw1b01|泰力S11系列零火智能开关一开|32390|
|taili.switch.sw1c01|泰力118AS单边键系列零火智能开关一开|32403|
|taili.switch.sw1d01|泰力118AS任意键系列零火智能开关一开|32410|
|taili.switch.sw1e01|泰力V1系列零火智能开关一开|32413|
|taili.switch.sw2a01|泰力ST7系列零火智能开关二开|31646|
|taili.switch.sw2b01|泰力S11系列零火智能开关二开|32391|
|taili.switch.sw2c01|泰力118AS单边键系列零火智能开关二开|32404|
|taili.switch.sw2d01|泰力118AS任意键系列零火智能开关二开|32411|
|taili.switch.sw2e01|泰力V1系列零火智能开关二开|32414|
|taili.switch.sw3a01|泰力ST7系列零火智能开关三开|31647|
|taili.switch.sw3b01|泰力S11系列零火智能开关三开|32392|
|taili.switch.sw3c01|泰力118AS单边键系列零火智能开关三开|32405|
|taili.switch.sw3d01|泰力118AS任意键系列零火智能开关三开|32412|
|taili.switch.sw3e01|泰力V1系列零火智能开关三开|32415|
|taili.switch.sw4b01|泰力S11系列零火智能开关四开|34045|
|taili.switch.sw4e01|泰力V1系列零火智能开关四开|34049|
|tew.switch.twkg1|泰沃智能开关Pro 单键|40197|
|tew.switch.twkg3|泰沃智能开关Pro 三键|40199|
|tew.switch.twkg4|泰沃智能开关Pro 四键|40200|
|tew.switch.twkgx2|泰沃智能开关Pro 双键|40286|
|tho.switch.sw1b01|THO特好智能墙壁开关（一开）|31959|
|tho.switch.sw2b01|THO特好智能墙壁开关（二开）|31960|
|tho.switch.sw3b01|THO特好智能墙壁开关（三开）|31961|
|tho.switch.sw4b01|THO特好智能墙壁开关（四开）|36829|
|thzn.switch.thkg1|天狐超薄开关T9Pro 一开 Mesh2.0|30165|
|thzn.switch.thkg2|天狐超薄开关T9Pro 二开 Mesh2.0|30166|
|thzn.switch.thkg3|天狐超薄开关T9Pro 三开 Mesh2.0|30167|
|thzn.switch.thkg4|天狐超薄开关T9Pro 四开 Mesh2.0|30168|
|tnv.switch.sw1b01|GAMDER V90彩屏一键开关|16992|
|tnv.switch.sw1c01|ZT 智能开关1键|18783|
|tnv.switch.sw1d01|ZT U6智能开关1键|23157|
|tnv.switch.sw1e01|ZT 智能单零火开关1键|23233|
|tnv.switch.sw1f01|ZT U6 Pro智能开关1键|24268|
|tnv.switch.sw2b01|GAMDER V90彩屏二键开关|16993|
|tnv.switch.sw2c01|ZT 智能开关2键|18784|
|tnv.switch.sw2d01|ZT U6智能开关2键|23158|
|tnv.switch.sw2e01|ZT 智能单零火开关2键|23234|
|tnv.switch.sw2f01|ZT U6 Pro智能开关2键|24269|
|tnv.switch.sw3b01|GAMDER V90彩屏三键开关|16994|
|tnv.switch.sw3c01|ZT 智能开关3键|18785|
|tnv.switch.sw3d01|ZT U6智能开关3键|23159|
|tnv.switch.sw3e01|ZT 智能单零火开关3键|23235|
|tnv.switch.sw3f01|ZT U6 Pro智能开关3键|24270|
|tnv.switch.sw4b01|GAMDER V90彩屏四键开关|16995|
|tnv.switch.sw4c01|ZT 智能开关4键|18786|
|tnv.switch.sw4f01|ZT U6 Pro智能开关4键|24271|
|tofan.switch.111h1|悠觅智能一键开关H1-MESH2.0|30760|
|tofan.switch.222h1|悠觅智能二键开关H1-MESH2.0|30761|
|tofan.switch.333h1|悠觅智能三键开关H1-MESH2.0|30762|
|tofan.switch.bln31|YOOMI一键开关Mesh2.0版|25311|
|tofan.switch.bln32|YOOMI二键开关Mesh2.0版|25312|
|tofan.switch.bln33|YOOMI三键开关Mesh2.0版|25313|
|tofan.switch.bln34|YOOMI四键开关Mesh2.0版|25314|
|tofan.switch.bln36|YOOMI六键开关Mesh2.0版|25315|
|tofan.switch.bln38|YOOMI八键开关Mesh2.0版|25316|
|tofan.switch.blswb1|悠觅超极岛一键彩屏开关|39635|
|tofan.switch.blswb2|悠觅超极岛二键彩屏开关|39636|
|tofan.switch.blswb3|悠觅超极岛三键彩屏开关|39637|
|tofan.switch.blswb4|悠觅超极岛四键彩屏开关|39638|
|tofan.switch.blswb6|悠觅超极岛六键彩屏开关|39639|
|tofan.switch.h1pro1|悠觅一键屏显开关H1-PRO2.0|30768|
|tofan.switch.h1pro2|悠觅二键屏显开关H1-PRO2.0|30767|
|tofan.switch.h1pro3|悠觅三键屏显开关H1-PRO2.0|30766|
|tofan.switch.pxln4|悠觅四键屏显开关D1|27791|
|tofan.switch.s01|YOOMI多功能开关Z1-Mesh版|19506|
|tofan.switch.ymd1|悠觅Z1屏显开关MESH2.0|28301|
|topwit.cs.rzw47|UZ插卡取电器|18257|
|topwit.plug.rzs01|UWIZE优智者智能安全轨道插|25380|
|topwit.plug.rzs02|IWN小铃铛智能安全轨道插|30515|
|topwit.remote.ru03|三位无线场景面板|10741|
|topwit.switch.bln01|一位零火Mesh开关|8042|
|topwit.switch.bln02|二位零火Mesh开关|8043|
|topwit.switch.bln03|三位零火Mesh开关|8044|
|topwit.switch.bln04|四位零火Mesh开关|10190|
|topwit.switch.iwnw01|UZ零火开关（一键）|22600|
|topwit.switch.iwnw02|UZ零火开关（二键）|22601|
|topwit.switch.iwnw03|UZ零火开关（三键）|22602|
|topwit.switch.rzw01|一位单火Mesh开关|5092|
|topwit.switch.rzw02|二位单火Mesh开关|5093|
|topwit.switch.rzw03|三位单火Mesh开关|5082|
|topwit.switch.rzw05|四位单火Mesh开关|12446|
|topwit.switch.rzw11|一位单火Mesh触摸开关|6409|
|topwit.switch.rzw12|二位单火Mesh触摸开关|6417|
|topwit.switch.rzw13|三位单火Mesh触摸开关|6418|
|topwit.switch.rzw24|智能开关单火一位（Mesh）|15034|
|topwit.switch.rzw25|智能开关单火二位（Mesh）|15035|
|topwit.switch.rzw28|智能开关单火三位（Mesh）|15060|
|topwit.switch.rzw30|智能开关单火四位（Mesh）|15075|
|topwit.switch.rzw31|智能开关零火一位（Mesh）|15079|
|topwit.switch.rzw32|智能开关零火二位（Mesh）|15080|
|topwit.switch.rzw33|智能开关零火三位（Mesh）|15081|
|topwit.switch.rzw34|智能开关零火四位（Mesh）|15082|
|topwit.switch.rzw43|UZ一位零火开关|17260|
|topwit.switch.rzw44|UZ二位零火开关|17261|
|topwit.switch.rzw45|UZ三位零火开关|17262|
|topwit.switch.rzw46|UZ四位零火开关|17263|
|topwit.switch.rzw49|UZ一位零火开关|19562|
|topwit.switch.rzw50|UZ二位零火开关|19563|
|topwit.switch.rzw51|UZ三位零火开关|19574|
|topwit.switch.rzw52|UZ四位零火开关|19575|
|topwit.switch.rzw59|UZ四位单零火兼容开关|21140|
|topwit.switch.rzw61|UZ三位单零火兼容开关|22496|
|topwit.switch.rzw62|UZ二位单零火兼容开关|22497|
|topwit.switch.rzw63|UZ一位单零火兼容开关|22498|
|topwit.switch.rzw64|UZ一位零火屏显开关|22973|
|topwit.switch.rzw65|UZ二位零火屏显开关|23088|
|topwit.switch.rzw66|UZ三位零火屏显开关|23089|
|topwit.switch.rzw67|UZ四位零火屏显开关|23090|
|topwit.switch.rzw71|UWIZE优智者圆屏智能多功能面板|24616|
|topwit.switch.rzw72|UWIZE优智者全面屏智能面板开关|24871|
|topwit.switch.rzw73|UWIZE优智者六位场景复合开关|24955|
|topwit.switch.rzw74|IWN小铃铛圆屏智能多功能面板|25814|
|topwit.switch.rzw75|IWN小铃铛全面屏智能面板|25815|
|topwit.switch.rzw77|IWN小铃铛一位零火智能开关|27516|
|topwit.switch.rzw78|IWN小铃铛二位零火智能开关|27517|
|topwit.switch.rzw79|IWN小铃铛三位零火智能开关|27518|
|topwit.switch.rzw80|IWN小铃铛四位零火智能开关|27519|
|topwit.switch.rzw81|UWIZE优智者一位零火智能开关|28040|
|topwit.switch.rzw82|UWIZE优智者二位零火智能开关|28042|
|topwit.switch.rzw83|UWIZE优智者三位零火智能开关|28043|
|topwit.switch.rzw84|UWIZE优智者一位零火屏显开关|29655|
|topwit.switch.rzw85|UWIZE优智者二位零火屏显开关|29656|
|topwit.switch.rzw86|UWIZE优智者三位零火屏显开关|29657|
|topwit.switch.rzw87|UWIZE优智者四位零火屏显开关|29658|
|topwit.switch.rzw88|IWN小铃铛一位零火屏显开关|29659|
|topwit.switch.rzw89|IWN小铃铛三位零火屏显开关|29660|
|topwit.switch.rzw90|IWN小铃铛二位零火屏显开关|29661|
|topwit.switch.rzw91|IWN小铃铛四位零火屏显开关|29662|
|topwit.switch.rzw96|UWIZE优智者二位单零火兼容开关|29667|
|topwit.switch.rzw98|UWIZE优智者四位单零火兼容开关|29670|
|topwit.switch.rzw99|IWN小铃铛一位单零火兼容开关|29882|
|topwit.switch.yzw01|IWN小铃铛二位单零火兼容开关|29883|
|topwit.switch.yzw02|IWN小铃铛三位单零火兼容开关|29884|
|topwit.switch.yzw03|IWN小铃铛四位单零火兼容开关|29885|
|topwit.switch.yzw04|UWIZE优智者一位单零火兼容开关|29923|
|topwit.switch.yzw05|UWIZE优智者三位单零火兼容开关|29924|
|topwit.switch.yzw06|UWIZE优智者四位零火智能开关|29925|
|tpzn.switch.9999|桐鹏智能通断器|20618|
|trzn.switch.zntdq|QEEX智能通断器|36868|
|tsd.plug.hmi001|通士达插座|4950|
|tuodi.switch.tdwtdq|拓迪电计量通断器（WiFi）|34482|
|uimeen.switch.tdq1|钻石通断器Mesh2.0|28081|
|unec.switch.sw1a01|UNEC一位蓝牙复合开关|31805|
|unec.switch.sw2a01|UNEC二位蓝牙复合开关|31806|
|unec.switch.sw3a01|UNEC三位蓝牙复合开关|31807|
|unec.switch.sw4a01|UNEC四位3路带屏蓝牙复合开关|31808|
|uwize.cs.yzw16|UWIZE优智者插卡取电器|36757|
|uwize.plug.yzs01|UWIZE优智者智能计量插座|34012|
|uwize.switch.yzw06|UWIZE优智者彩屏按键三位零火智能开关|33256|
|uwize.switch.yzw07|UWIZE优智者彩屏按键二位零火智能开关|33257|
|uwize.switch.yzw08|UWIZE优智者彩屏按键一位零火智能开关|33258|
|uwize.switch.yzw09|UWIZE优智者彩屏按键四位零火智能开关|33631|
|uwize.switch.yzw10|UWIZE优智者屏显免刻字一位零火智能开关|34423|
|uwize.switch.yzw11|UWIZE优智者屏显免刻字二位零火智能开关|34424|
|uwize.switch.yzw12|UWIZE优智者屏显免刻字三位零火智能开关|34425|
|uwize.switch.yzw13|UWIZE优智者屏显免刻字四位零火智能开关|34426|
|uwize.switch.yzw15|UWIZE优智者四位零火智能开关Mesh2.0|35356|
|uwize.switch.yzw16|UWIZE优智者四位单零火兼容智能开关|35357|
|uwize.switch.yzw23|UWIZE优智者全面屏智能面板开关|38497|
|vbocga.switch.sw1a01|唯宝彩佳风华一位开关F1H-PC|31743|
|vbocga.switch.sw2a01|唯宝彩佳风华二位开关F2H-PC|31742|
|vbocga.switch.sw2b01|唯宝彩佳灵动岛二位开关D2-PC|37396|
|vbocga.switch.sw3a01|唯宝彩佳风华三位开关F3H-PC|31741|
|vbocga.switch.sw3a03|唯宝彩佳智能屏幕开关Zao0102|35726|
|vbocga.switch.sw4a01|唯宝彩佳风华四位开关F4H-PC|31740|
|vbocga.switch.sw4b01|唯宝彩佳灵动岛四位开关D4-PC|35012|
|vbocga.switch.sw8a01|唯宝彩佳风华八位开关F8S-PC|31964|
|viomi.controller.pads|云米AI智能控制面板HomePad|79111|
|viomi.switch.nm1|云米AI智能开关Master（零火一键）|20155|
|viomi.switch.nm2|云米AI智能开关Master（零火二键）|20156|
|viomi.switch.nm3|云米AI智能开关Master（零火三键）|20157|
|wainft.switch.sw0a01| 馨光蓝牙mesh通断器|3150|
|wainft.switch.sw0a02|XG蓝牙Mesh通断器|4380|
|wainft.switch.sw3a01|XG蓝牙Mesh智能开关|7831|
|wanduo.switch.sw1a01|WD智能一键开关|34195|
|wanduo.switch.sw2a01|WD智能二键开关|34196|
|wanduo.switch.sw3a01|WD智能三键开关|34197|
|wanduo.switch.sw4a01|WD智能四键开关|37748|
|wfxx.plug.pdczwf|PD智能插座(WiFi)|15581|
|wfxx.relay.asdasd|PD通断器(WiFi)|13866|
|wgse.switch.sw1a01|WGSE智能开关1键|32684|
|wgse.switch.sw1b01|WGSE智能屏显开关1键|36179|
|wgse.switch.sw1c01|WGSE智能开关单零火1键|36554|
|wgse.switch.sw1r01|WGSE智能彩屏开关1键|37972|
|wgse.switch.sw2a01|WGSE智能开关2键|32686|
|wgse.switch.sw2b01|WGSE智能屏显开关2键|36180|
|wgse.switch.sw2c01|WGSE智能开关单零火2键|36555|
|wgse.switch.sw2r01|WGSE智能彩屏开关2键|37973|
|wgse.switch.sw3a01|WGSE智能开关3键|32687|
|wgse.switch.sw3a03|WGSE情景智慧屏开关|36167|
|wgse.switch.sw3b01|WGSE智能屏显开关3键|36181|
|wgse.switch.sw3c01|WGSE智能开关单零火3键|36556|
|wgse.switch.sw3r01|WGSE智能彩屏开关3键|37974|
|wgse.switch.sw4a01|WGSE智能屏显开关|32688|
|wgse.switch.sw4a02|WGSE智能开关4键|36663|
|wgse.switch.sw4r01|WGSE智能彩屏开关4键|37975|
|whdz.plug.001|奥多朗屏显智能轨道排插S2|24581|
|wiing.plug.bm1|AImLbS智能插座(mesh)|30660|
|wiing.plug.jdlpro|AImLbS智能插座安全守护版|36535|
|wiing.plug.jdls1|AImLbS智能插座(WiFi)|30513|
|wiing.plug.v7icm|AlmLbS智能插座（Mesh）|28006|
|wiing.plug.v8icm|AlmLbS智能插座计量版（Mesh）|28005|
|wiing.plug.v9icm|AlmLbs智能插座（WiFi）|32254|
|wiing.plug.zljcz1|宅联界智能插座（Mesh）|38752|
|wiing.switch.zljtd2|宅联界智能通断器（Mesh）|39078|
|wise.switch.sw2a01|WISE情景智慧屏开关|16722|
|wiser.switch.hjp002|施耐德电气玻璃智能4寸全面屏中控面板开关|36895|
|wiser.switch.hsk005|施耐德电气智能一位一场景零火开关|36418|
|wiser.switch.hsk006|施耐德电气智能二位二场景零火开关|36419|
|wiser.switch.hsk007|施耐德电气智能三位三场景零火开关|36420|
|wiser.switch.hsk008|施耐德电气智能二位四场景零火开关|36421|
|wiser.switch.hyk005|施耐德电气智能一位零火开关|36455|
|wiser.switch.hyk006|施耐德电气智能二位零火开关|36456|
|wiser.switch.hyk007|施耐德电气智能三位零火开关|36457|
|wiser.switch.hyk008|施耐德电气智能四位零火开关|36458|
|wiser.switch.hyk009|施耐德电气玻璃智能一位零火开关|36463|
|wiser.switch.hyk010|施耐德电气玻璃智能二位零火开关|36464|
|wiser.switch.hyk011|施耐德电气玻璃智能三位零火开关|36465|
|wiser.switch.hyk012|施耐德电气玻璃智能四位零火开关|36466|
|wiser.switch.hyk013|施耐德电气带屏智能一位带场景零火开关|36526|
|wiser.switch.hyk014|施耐德电气带屏智能二位带场景零火开关|36527|
|wiser.switch.hyk015|施耐德电气带屏智能三位带场景零火开关|36528|
|wiser.switch.hyk016|施耐德电气带屏智能四位带场景零火开关|36529|
|wiser.switch.hyk017|施耐德电气玻璃带屏智能一位带场景零火开关|36658|
|wiser.switch.hyk018|施耐德电气玻璃带屏智能二位带场景零火开关|36660|
|wiser.switch.hyk019|施耐德电气玻璃带屏智能三位带场景零火开关|36661|
|wiser.switch.hyk020|施耐德电气玻璃带屏智能四位带场景零火开关|36833|
|wlg.switch.sw1a01|WLG-U9 智能开关一键|28280|
|wlg.switch.sw2a01|WLG-U9 智能开关二键|28281|
|wlg.switch.sw2b01|WLG-U9Pro 圆屏开关二键|28294|
|wlg.switch.sw3a01|WLG-U9 智能开关三键|28282|
|wlg.switch.sw3b01|WLG-U9Pro 圆屏开关三键|28295|
|wlg.switch.sw4b01|WLG-U9Pro 圆屏开关四键|28296|
|wxal.switch.z51k|狮朗盾Z5一键屏显开关|38699|
|wxal.switch.z52k|狮朗盾Z5二键屏显开关|38700|
|wxal.switch.z53k|狮朗盾Z5三键屏显开关|38701|
|wzojdz.switch.bjtdq5|巨欧智能通断器WiFi版|28990|
|wzojdz.switch.tdq1|巨欧智能通断器Mesh2.0|33461|
|wzojdz.switch.tdq3|巨欧智能通断器Mesh版|28991|
|xdx001.plug.pc01|FDD 国际电工智能轨道插座|39490|
|xdx001.switch.dh4k|fdd 国际电工四键智能开关|39108|
|xdx001.switch.dlh1k|fdd 国际电工一键智能开关|39105|
|xdx001.switch.dlh2k|fdd 国际电工二键智能开关|39106|
|xdx001.switch.dlh3k|fdd 国际电工三键智能开关|39107|
|xdx001.switch.px01|fdd 国际电工一键屏显开关|35592|
|xdx001.switch.px02|fdd 国际电工二键屏显开关|35593|
|xdx001.switch.px03|fdd 国际电工三键屏显开关|35594|
|xdx001.switch.sw1a01|fdd 国际电工智能一键开关|34114|
|xdx001.switch.sw1b01|fdd 国际电工智联一键开关|34850|
|xdx001.switch.sw2a01|fdd 国际电工智能二键开关|34115|
|xdx001.switch.sw2b01|fdd 国际电工智联二键开关|34849|
|xdx001.switch.sw3a01|fdd 国际电工智能三键开关|34116|
|xdx001.switch.sw3b01|fdd 国际电工智联三键开关|34848|
|xdx001.switch.sw4a01|fdd 国际电工智能四键开关|34117|
|xdx001.switch.sw4b01|fdd 国际电工智联四键开关|34847|
|xhuan.plug.gdc01|苏米安全轨道插座Mesh2.0|30851|
|xhuan.remote.smwx1|苏米无线开关|38161|
|xhuan.remote.smxn4|苏米无线旋钮开关|38739|
|xhuan.switch.1lrz02|苏米智能开关H（单火一键）|14650|
|xhuan.switch.1lrz04|苏米智能开关Mesh2.0（单零火一键）|25010|
|xhuan.switch.1nrz02|苏米智能开关H（零火一键）|14859|
|xhuan.switch.1nrz03|苏米智能开关Hs（零火一键）|21907|
|xhuan.switch.1nrz05|苏米智能开关Mesh2.0（零火一键）|27351|
|xhuan.switch.1prz01|苏米屏显开关Mesh2.0(单键)|24516|
|xhuan.switch.1prz02|苏米趣动屏开关S1（单键）|35161|
|xhuan.switch.1prz03|苏米智能开关Air（零火单键）|36367|
|xhuan.switch.2lrz02|苏米智能开关H（单火二键）|14649|
|xhuan.switch.2lrz04|苏米智能开关Mesh2.0（单零火二键）|25011|
|xhuan.switch.2nrz02|苏米智能开关H（零火二键）|14860|
|xhuan.switch.2nrz03|苏米智能开关Hs（零火二键）|21908|
|xhuan.switch.2nrz05|苏米智能开关Mesh2.0（零火二键）|27352|
|xhuan.switch.2prz01|苏米屏显开关Mesh2.0(双键)|24517|
|xhuan.switch.2prz02|苏米趣动屏开关S1（双键）|35162|
|xhuan.switch.2prz03|苏米智能开关Air（零火双键）|36368|
|xhuan.switch.3lrz02|苏米智能开关H（单火三键）|14604|
|xhuan.switch.3lrz04|苏米智能开关Mesh2.0（单零火三键）|25012|
|xhuan.switch.3nrz02|苏米智能开关H（零火三键）|14515|
|xhuan.switch.3nrz03|苏米智能开关Hs（零火三键）|21909|
|xhuan.switch.3nrz05|苏米智能开关Mesh2.0（零火三键）|27353|
|xhuan.switch.3prz01|苏米屏显开关Mesh2.0(三键)|24518|
|xhuan.switch.3prz02|苏米趣动屏开关S1（三键）|35163|
|xhuan.switch.3prz03|苏米智能开关Air（零火三键）|36369|
|xhuan.switch.4lrz02|苏米智能开关H（单火四键）|14727|
|xhuan.switch.4lrz04|苏米智能开关Mesh2.0（单零火四键）|25014|
|xhuan.switch.4nrz02|苏米智能开关H（零火四键）|14858|
|xhuan.switch.4nrz03|苏米智能开关Hs（零火四键）|21910|
|xhuan.switch.4nrz05|苏米智能开关Mesh2.0（零火四键）|27354|
|xhuan.switch.4prz01|苏米屏显开关Mesh2.0(四键)|24519|
|xhuan.switch.4prz02|苏米趣动屏开关S1（四键）|35164|
|xhuan.switch.4prz03|苏米智能开关Air（零火四键）|36370|
|xhuan.switch.h1p1|苏米屏显开关Y1 Pro（单键）|32017|
|xhuan.switch.h1p2|苏米屏显开关Y1 Pro（双键）|32018|
|xhuan.switch.h1p3|苏米屏显开关Y1 Pro（三键）|32019|
|xhuan.switch.plcg02|苏米智能开关PLC版(单键)|80885|
|xhuan.switch.plcg03|苏米智能开关PLC版(双键)|80886|
|xhuan.switch.plcg04|苏米智能开关PLC版(三键)|80887|
|xhuan.switch.plcg05|苏米智能开关PLC版(四键)|80888|
|xhuan.switch.sw1a01|苏米T1智能开关（零火单键）|5833|
|xhuan.switch.sw1b01|苏米智能开关（零火一键）|13509|
|xhuan.switch.sw2a01|苏米T1智能开关（零火双键）|5834|
|xhuan.switch.sw2b01|苏米智能开关（零火二键）|13510|
|xhuan.switch.sw2c02|苏米全面屏开关|15973|
|xhuan.switch.sw3a01|苏米T1智能开关（零火三键）|5835|
|xhuan.switch.sw3b01|苏米智能开关（零火三键）|13511|
|xhuan.switch.sw3c03|苏米全面屏开关Mesh2.0|31071|
|xhuan.switch.sw4b01|苏米智能开关（零火四键）|13512|
|xhuan.switch.sw8a01|苏米缤纷面板|11126|
|xhuan.switch.xlrz05|苏米智能圆屏面板Mesh2.0|26205|
|xhzn88.switch.xks01|星凯思智能开关一开（Mesh2.0）|28261|
|xhzn88.switch.xks02|星凯思智能开关二开（Mesh2.0）|28260|
|xhzn88.switch.xks03|星凯思智能开关三开（Mesh2.0）|28259|
|xiaol.plug.v9icm|XLTL智能控制器|27437|
|xiaomi.plug.01qm|小米轨道插座10A智能插座适配器|18798|
|xiaomi.plug.10ahyb|小米轨道插座10A智能插座适配器|26038|
|xiaomi.plug.2pro|小米智能墙壁插座Pro|21507|
|xiaomi.plug.2wpro|小米智能墙壁插座Pro|21508|
|xiaomi.plug.mcn001|小米智能墙壁插座Pro|13521|
|xiaomi.plug.mcn003|小米智能墙壁插座Pro|17885|
|xiaomi.plug.mcn005|小米智能墙壁插座|28248|
|xiaomi.plug.test1|测试模拟插座|10|
|xiaomi.remote.mcn002|小米智能无线开关（双开）|22888|
|xiaomi.remote.mcn003|小米智能无线开关（双开）|28247|
|xiaomi.remote.o635yz|磁吸物理按键|20256|
|xiaomi.switch.2b1|小米智能开关Pro 2026版（单开）|33175|
|xiaomi.switch.2b2|小米智能开关Pro 2026版（双开）|33178|
|xiaomi.switch.2b3|小米智能开关Pro 2026版（三开）|33180|
|xiaomi.switch.2pro|小米智能开关2 Pro（单开）|35632|
|xiaomi.switch.2pro1|小米智能开关Pro（单开）|21502|
|xiaomi.switch.2pro2|小米智能开关Pro（双开）|21501|
|xiaomi.switch.2pro22|小米智能开关2 Pro（双开）|35633|
|xiaomi.switch.2pro23|小米智能开关2 Pro（三开）|35634|
|xiaomi.switch.2pro2h|小米智能开关2 Pro（双开）|35636|
|xiaomi.switch.2pro3|小米智能开关Pro（三开）|21500|
|xiaomi.switch.2pro3h|小米智能开关2 Pro（三开）|35637|
|xiaomi.switch.2proh|小米智能开关2 Pro（单开）|35635|
|xiaomi.switch.2w1|小米智能开关Pro 2026版（单开）|33174|
|xiaomi.switch.2w2|小米智能开关Pro 2026版（双开）|33176|
|xiaomi.switch.2w3|小米智能开关Pro 2026版（三开）|33179|
|xiaomi.switch.2wpro1|小米智能开关Pro（单开）|21505|
|xiaomi.switch.2wpro2|小米智能开关Pro（双开）|21504|
|xiaomi.switch.2wpro3|小米智能开关Pro（三开）|21503|
|xiaomi.switch.a2ota|万能遥控器|70047|
|xiaomi.switch.pro1|小米智能开关Pro（单开）|14431|
|xiaomi.switch.pro2|小米智能开关Pro（双开）|14432|
|xiaomi.switch.pro3|小米智能开关Pro（三开）|14433|
|xiaomi.switch.w1|小米智能开关（单开）|21606|
|xiaomi.switch.w1b|小米智能开关（单开）|28244|
|xiaomi.switch.w2|小米智能开关（双开）|21607|
|xiaomi.switch.w2b|小米智能开关（双开）|28245|
|xiaomi.switch.w3|小米智能开关（三开）|21608|
|xiaomi.switch.w3b|小米智能开关（三开）|28246|
|xiaomi.switch.wb1|小米智能开关2（单开）|34451|
|xiaomi.switch.wb2|小米智能开关2（双开）|34452|
|xiaomi.switch.wb3|小米智能开关2（三开）|34453|
|xiaomi.switch.wpro1|小米智能开关Pro（单开）|17767|
|xiaomi.switch.wpro2|小米智能开关Pro（双开）|17768|
|xiaomi.switch.wpro3|小米智能开关Pro（三开）|17769|
|xiaomi.switch.ww1|小米智能开关2（单开）|34447|
|xiaomi.switch.ww2|小米智能开关2（双开）|34449|
|xiaomi.switch.ww3|小米智能开关2（三开）|34450|
|xinji.switch.sw1a02|新极智能一键开关Pro|18633|
|xinji.switch.sw1b01|新极智能一路开关Pro2.0|22939|
|xinji.switch.sw2a02|新极智能二键开关Pro|18634|
|xinji.switch.sw2b01|新极智能二路开关Pro2.0|22940|
|xinji.switch.sw3a02|新极智能三键开关Pro|18635|
|xinji.switch.sw3b01|新极智能三路开关Pro2.0|22941|
|xinji.switch.sw4a02|新极智能四键开关Pro|18363|
|xinji.switch.sw4b01|新极智能四路开关Pro2.0|22942|
|xiubo.switch.sw1a01|秀柏照明智能开关一键|31894|
|xiubo.switch.sw2a01|秀柏照明智能开关二键|31893|
|xiubo.switch.sw3a01|秀柏照明智能开关三键|31892|
|xiubo.switch.sw4a01|秀柏照明智能开关四键|31890|
|xjzn.plug.v9xjw|鑫居智能转换插座(WiFi)|32065|
|xjzn.switch.xjtdq9|鑫居智能通断器（Mesh）|38638|
|xl2024.plug.xlkjk|Pluslife电脑开机卡|27050|
|xmd.switch.sw1a01|星明浩智能开关面板A6 一开|28761|
|xmd.switch.sw2a01|星明浩智能开关面板A6 二开|28762|
|xmd.switch.sw2d03|星明浩智慧屏开关S4|17782|
|xmd.switch.sw3a01|星明浩智能开关面板A6 三开|28768|
|xmd.switch.sw3a03|星明浩智慧情景开关屏A6 三开|36454|
|xmd.switch.sw3d03|星美达智慧屏开关S4|20556|
|xmd.switch.sw4a02|星明浩智能屏显开关面板A6 四开|28767|
|xmd.switch.sw4a03|星明浩智能开关面板A6 四开|37217|
|xry.switch.sw1b01|星如雨智能开关（一键）|27321|
|xry.switch.sw2b01|星如雨智能开关（二键）|27322|
|xry.switch.sw3b01|星如雨智能开关（三键）|27323|
|xry.switch.sw4b01|星如雨智能开关（四键）|27324|
|xunwei.switch.bpns4|XW四键屏显开关M8-Pro|24079|
|xwa.switch.bln01|小蛙智能一键开关|31097|
|xwa.switch.bln02|小蛙智能二键开关|31098|
|xwa.switch.bln03|小蛙智能三键开关|31099|
|xwa.switch.bln04|小蛙智能四键开关|31100|
|xwiwn.plug.xwp001|xiaowell小为科技智能计量插座|34943|
|xwiwn.switch.xwk001|xiaowell小为科技屏显免刻字一位零火智能开关|33863|
|xwiwn.switch.xwk002|xiaowell小为科技屏显免刻字二位零火智能开关|33864|
|xwiwn.switch.xwk003|xiaowell小为科技屏显免刻字三位零火智能开关|33865|
|xwiwn.switch.xwk004|xiaowell小为科技屏显免刻字四位零火智能开关|33866|
|xwiwn.switch.xwk005|xiaowell小为科技一位零火智能开关|34490|
|xwiwn.switch.xwk006|xiaowell小为科技二位零火智能开关|34491|
|xwiwn.switch.xwk007|xiaowell小为科技三位零火智能开关|34492|
|xwiwn.switch.xwk008|xiaowell小为科技四位零火智能开关|34493|
|xwiwn.switch.xwk009|xiaowell小为科技一位单零火兼容智能开关|34494|
|xwiwn.switch.xwk010|xiaowell小为科技二位单零火兼容智能开关|34495|
|xwiwn.switch.xwk011|xiaowell小为科技三位单零火兼容智能开关|34496|
|xwiwn.switch.xwk012|xiaowell小为科技四位单零火兼容智能开关|34497|
|xwiwn.switch.xwk013|xiaowell小为科技彩屏按键一位零火智能开关|34498|
|xwiwn.switch.xwk014|xiaowell小为科技彩屏按键二位零火智能开关|34499|
|xwiwn.switch.xwk015|xiaowell小为科技彩屏按键三位零火智能开关|34500|
|xwiwn.switch.xwk016|xiaowell小为科技彩屏按键四位零火智能开关|34723|
|xwiwn.switch.xwk017|xiaowell小为科技全面屏智能面板开关|40071|
|yankon.switch.sw01|阳光智能开关单键|27828|
|yankon.switch.sw02|阳光智能开关双键|27827|
|yankon.switch.sw03|阳光智能开关三键|27826|
|yankon.switch.ykpx01|阳光智能开关单键M3|32169|
|yankon.switch.ykpx02|阳光智能开关双键M3|32168|
|yankon.switch.ykpx03|阳光智能开关三键M3|32167|
|yankon.switch.ykpx04|阳光智能开关四键M3|32166|
|ydhome.switch.s1|优点智能蓝牙Mesh开关面板 三开|2385|
|ydhome.switch.s2|优点智能蓝牙Mesh开关面板 二开|2448|
|ydhome.switch.s3|优点智能蓝牙Mesh开关面板 一开|2500|
|ydsemi.switch.cz03|智悦智能插座|10581|
|yeelink.controller.v2|Yeelight S21 全面屏开关|71518|
|yeelink.plug.plug1|Yeelight T1系列智能轨道插座|26150|
|yeelink.plug.plug2|Yeelight T1系列智能轨道插座Lite|39044|
|yeelink.remote.contrl|小米无线开关（双键版）|6473|
|yeelink.remote.remote|Yeelight 无线开关S1|1983|
|yeelink.remote.sw1|Yeelight 智能无线开关（单键）|16494|
|yeelink.remote.sw2|Yeelight 智能无线开关（双键）|16495|
|yeelink.remote.sw3|Yeelight情景开关（无线版）|21801|
|yeelink.remote.sw4|Yeelight情景开关（无线六键）|21802|
|yeelink.remote.swd5|Yeelight 情景开关（无线四键）|21222|
|yeelink.remote.yrm02|Yeelight Pro 八键控制面板|73193|
|yeelink.remote.yrm03|Yeelight Pro 四键控制面板|73484|
|yeelink.remote.yrm04|Yeelight Pro 六键控制面板|73485|
|yeelink.remote.yrm05|Yeelight Pro 旋钮遥控器|73486|
|yeelink.remote.yrm06|Yeelight 情景开关（六键）|12611|
|yeelink.switch.sw1|Yeelight 双路控制模块|2299|
|yeelink.switch.sw11|Yeelight 智能开关（一开）|23396|
|yeelink.switch.sw12|Yeelight 智能开关（二开）|23397|
|yeelink.switch.sw13|Yeelight 智能开关（三开）|23398|
|yeelink.switch.sw14|Yeelight 智能开关（四开）|23399|
|yeelink.switch.sw16|Yeelight Z2智能开关(屏显四键)|27145|
|yeelink.switch.sw18|Yeelight全面屏开关|30046|
|yeelink.switch.sw19|Yeelight T1智能开关(屏显四键)|36956|
|yeelink.switch.sw20|Yeelight K2智能开关(屏显四键)|36957|
|yeelink.switch.sw3|YEELIGHT凌动 智能开关（一键）|17292|
|yeelink.switch.sw4|YEELIGHT凌动 智能开关（二键）|17293|
|yeelink.switch.sw5|YEELIGHT凌动 智能开关（三键）|17294|
|yeelink.switch.sw6|YEELIGHT凌动 智能开关（四键）|17295|
|yeelink.switch.swd1|Yeelight 智能开关（零火单键）|19958|
|yeelink.switch.swd2|Yeelight 智能开关（零火双键）|19959|
|yeelink.switch.swd3|Yeelight 智能开关（零火三键）|19960|
|yeelink.switch.szsw1|Yeelight智能开关 C1（单键）|9927|
|yeelink.switch.szsw2|Yeelight智能开关 C1（双键）|9928|
|yeelink.switch.szsw3|Yeelight智能开关 C1（三键）|9929|
|yeelink.switch.v3|YEELIGHT凌动 智能中控屏开关|17296|
|yeelink.switch.ylsw4|Yeelight 智能开关（单键）|12455|
|yeelink.switch.ylsw5|Yeelight 智能开关（双键）|12456|
|yeelink.switch.ylsw6|Yeelight 智能开关（三键）|12457|
|yeelink.switch.ylsw7|Yeelight 智能开关（四键）|12458|
|yeelink.switch.ysw01|Yeelight Pro 智能开关（单键）|5622|
|yeelink.switch.ysw02|Yeelight Pro 智能开关（双键）|73480|
|yeelink.switch.ysw03|Yeelight Pro 智能开关（三键）|73481|
|yeelink.switch.ysw05|Yeelight Pro 双路通断器|7641|
|yeelink.switch.ysw11|Yeelight Pro 智能开关|84257|
|yeelink.switch.z1pro1|Yeelight 智能开关Pro (单键)|16316|
|yeelink.switch.z1pro2|Yeelight 智能开关Pro (双键)|16318|
|yeelink.switch.z1pro3|Yeelight 智能开关Pro (三键)|16319|
|yeelink.switch.z1pro4|Yeelight 智能开关Pro (四键)|16320|
|yg1.switch.sw1a01|情景轻触智能开关一位|28612|
|yg1.switch.sw2a01|情景轻触智能开关二位|28613|
|yg1.switch.sw3a01|情景轻触智能开关三位|28614|
|yg1.switch.sw4a01|情景轻触智能开关四位|28615|
|ygzm.switch.sw1a01|杜蒙智能开关Mesh2.0（零火一开）|35383|
|ygzm.switch.sw2a01|杜蒙智能开关Mesh2.0（零火二开）|35391|
|ygzm.switch.sw3a01|杜蒙智能开关Mesh2.0（零火三开）|35392|
|yhmesh.remote.sw1b01|缘弧旋钮无线开关|30462|
|yhmesh.switch.sw1a01|缘弧智能开关面板一键 V2s pro 2.0|27340|
|yhmesh.switch.sw2a01|缘弧智能开关面板二键 V2s pro 2.0|27341|
|yhmesh.switch.sw3a01|缘弧智能开关面板三键 V2s pro 2.0|27342|
|yhmesh.switch.sw4a01|缘弧智能开关面板四键 V2s pro 2.0|27343|
|yhope.remote.yhwx1|YHOPE 八键无线开关|33275|
|yhope.remote.yhwx2|YHOPE 六键无线开关|33276|
|yhope.switch.yhkg|YHOPE 二键1+1复合开关|31114|
|yhope.switch.yhkg2|YHOPE 四键2+2复合开关|31115|
|yhope.switch.yhkg3|YHOPE 六键3+3复合开关|31116|
|yhope.switch.yhkg4|YHOPE 四路复合开关|31117|
|yhope.switch.yhkg6|YHOPE 六键4+2复合开关|33611|
|yhope.switch.yhkg8|YHOPE 八键4+4复合开关|33612|
|ykcn.relay.rdcbl|YKCN智能剩余电流动作断路器|13290|
|ykcn.switch.cbcsmj|Wi-Fi智能导轨式通断器YKCN|15105|
|ykiot.switch.bln31|云控侠智能一键开关|26549|
|ykiot.switch.bln32|云控侠智能二键开关|26550|
|ykiot.switch.bln33|云控侠智能三键开关|26551|
|ykiot.switch.bln34|云控侠智能四键开关|26552|
|ykiot.switch.bln36|云控侠智能六键开关|26553|
|ykiot.switch.sw1a01|云控侠情景Mesh一键开关Ultra|26528|
|ykiot.switch.sw2a01|云控侠情景Mesh二键开关Ultra|26529|
|ykiot.switch.sw3a01|云控侠情景Mesh三键开关Ultra|26530|
|ykiot.switch.sw4a01|云控侠情景Mesh四键开关Ultra|26531|
|ykl.cs.swk01|晶米智能插卡取电mesh版|30013|
|ykl.switch.sw1a01|晶米一键智能开关mesh版|29774|
|ykl.switch.sw2a01|晶米二键智能开关mesh版|29775|
|ykl.switch.sw3a01|晶米三键智能开关mesh版|29777|
|ykl.switch.sw4a01|晶米四键智能开关mesh版|29778|
|ykl.switch.sw6a01|晶米六键智能开关mesh版|24190|
|ym001.plug.ymcz|炎米智能插座|33277|
|yoogee.switch.ygkg1|优阁智能一路开关（Mesh2.0）|31083|
|yoogee.switch.ygkg2|优阁智能二路开关（Mesh2.0）|31082|
|yoogee.switch.ygkg3|优阁智能三路开关（Mesh2.0）|31081|
|yoogee.switch.ygkg4|优阁智能四路开关（Mesh2.0）|31079|
|yoohoo.cs.ck01|FRFOX-M6智能插卡取电器|24003|
|yoohoo.switch.bln31|FRFOX蓝牙一键开关|22197|
|yoohoo.switch.bln311|FRFOX-M6一键智能开关|25429|
|yoohoo.switch.bln32|FRFOX蓝牙二键开关|22198|
|yoohoo.switch.bln322|FRFOX-M6二键智能开关|25430|
|yoohoo.switch.bln33|FRFOX蓝牙三键开关|22199|
|yoohoo.switch.bln333|FRFOX-M6三键智能开关|25431|
|yoohoo.switch.bln34|FRFOX蓝牙四键开关|22200|
|yoohoo.switch.bln344|FRFOX-M6四键智能开关|25432|
|yoohoo.switch.bln36|FRFOX蓝牙六键开关|22332|
|yoohoo.switch.bln366|FRFOX-M6六键智能开关|25433|
|yoohoo.switch.bln38|FRFOX蓝牙八键开关|22438|
|yoohoo.switch.s51k|FRFOX-S5一键智能开关|32091|
|yoohoo.switch.s52k|FRFOX-S5二键智能开关|32092|
|yoohoo.switch.s53k|FRFOX-S5三键智能开关|32093|
|yoohoo.switch.s54k|FRFOX-S5四键智能开关|32094|
|yoohoo.switch.s56k|FRFOX-S5六键智能开关|32095|
|yoohoo.switch.s701|FRFOX-S7一键智能开关|26555|
|yoohoo.switch.s702|FRFOX-S7二键智能开关|26556|
|yoohoo.switch.s703|FRFOX-S7三键智能开关|26557|
|yoohoo.switch.sw3a03|FRFOX-Z5臻薄四寸屏显开关|32428|
|yoohoo.switch.z501|FRFOX-Z5臻薄屏显一键开关|28675|
|yoohoo.switch.z502|FRFOX-Z5臻薄屏显二键开关|28676|
|yoohoo.switch.z503|FRFOX-Z5臻薄屏显三键开关|28677|
|yoohoo.switch.z702|FRFOX-Z7二键智能开关|28673|
|yoohoo.switch.z703|FRFOX-Z7三键智能开关|28672|
|yoohoo.switch.z704|FRFOX-Z7四键智能开关|28671|
|yoohoo.switch.z706|FRFOX-Z7六键智能开关|28670|
|yunmi.switch.su1|云米AI智能开关Super（一键）|27674|
|yunmi.switch.su2|云米AI智能开关Super（二键）|27673|
|yunmi.switch.su3|云米AI智能开关Super（三键）|27672|
|yunmi.switch.su4|云米AI智能开关Super（四键）|27671|
|yutai.plug.bm1|禹泰电工Mesh插座|30664|
|yutai.plug.fsov7m|禹泰电工智能插座（Mesh）|26160|
|yutai.plug.fsov7w|禹泰电工智能插座（WiFi）|26161|
|yutai.plug.fsov8m|禹泰电工智能插座计量版（Mesh）|26162|
|yutai.plug.fsov8w|禹泰电工智能插座计量版（WiFi）|26163|
|yutai.plug.jdls1|禹泰电工WiFi计量插座|28888|
|yutai.plug.socn1|禹泰电工WiFi插座|28892|
|yutai.plug.yccz1|禹泰电工智能插座Mesh2.0|36310|
|yutai.switch.yttdq|禹泰电工Mesh智能通断器|38754|
|yyzn.switch.sw3a03|Ai home 智能屏幕开关|17400|
|yzjkj.plug.yzjkj|麒石远程电脑开机卡|26727|
|zagd.switch.dsnyk1|Dsny智能单路K1开关|26202|
|zagd.switch.dsnyk2|Dsny智能两路K2开关|26201|
|zagd.switch.dsnyk3|Dsny智能三路K3开关|26198|
|zair.switch.zsc02w|墨小七智能灯开关控制器|9725|
|zbmesh.switch.zbtdq|ZKZB智能通断器|36187|
|zerone.remote.lywx8|灵妖无线八键开关(BLE)|35922|
|zerone.switch.lykg1|灵妖智能一位通断器（Mesh2.0）|30595|
|zerone.switch.lykg2|灵妖智能二位通断器（Mesh2.0）|30596|
|zerone.switch.lykg3|灵妖智能三位通断器（Mesh2.0）|30597|
|zerone.switch.lykg4|灵妖智能四位通断器（Mesh2.0）|30598|
|zhefa.switch.bxm08|ZF 四联八键开关〔N7B〕|21491|
|zhefa.switch.cxm01|ZF 一位开关〔N7C〕|21485|
|zhefa.switch.cxm02|ZF 二位开关〔N7C〕|21484|
|zhefa.switch.cxm03|ZF 三位开关〔N7C〕|21483|
|zhefa.switch.cxm04|ZF 四位开关〔N7C〕|21482|
|zhefa.switch.cxmqj2|ZF 二联四键开关〔N7C〕|21494|
|zhefa.switch.cxmqj3|ZF 三联六键开关〔N7C〕|21493|
|zhefa.switch.dxm03|ZF 三位开关〔N7D〕|21487|
|zhefa.switch.zero11|ZF 一位智能开关〔N7-ZK01-AXM〕|20107|
|zhefa.switch.zero22|ZF 二位智能开关〔N7-ZK02-AXM〕|20106|
|zhefa.switch.zero33|ZF 三位智能开关〔N7-ZK03-AXM〕|20105|
|zhefa.switch.zero44|ZF 四位智能开关〔N7-ZK04-AXM〕|20104|
|zhemi.switch.bln001|小奕一键智能开关|29069|
|zhemi.switch.bln002|小奕二键智能开关|29070|
|zhemi.switch.bln003|小奕三键智能开关|29071|
|zhemi.switch.bln004|小奕四键智能开关|29072|
|zhemi.switch.bln006|小奕六键智能开关|29074|
|zhemi.switch.bln008|小奕八键智能开关|29073|
|zhiee.plug.tdq5|百将USB插座Mesh2.0|38622|
|zhiee.switch.bjtdq5|百将wifi通断器|30116|
|zhiee.switch.tdq3|USP国际电工通断器|28987|
|zhiee.switch.tdq4|百将Mesh2.0通断器|36339|
|zhiqin.switch.mij04|叶绿体G1智能墙壁开关（零火线单键）|4739|
|zhiqin.switch.mij05|叶绿体G1智能墙壁开关（零火线双键）|4740|
|zhiqin.switch.mij06|叶绿体G1智能墙壁开关（零火线三键）|4741|
|zhiqin.switch.x101|叶绿体G1智能墙壁开关（单火线单键）|5245|
|zhiqin.switch.x102|叶绿体G1智能墙壁开关（单火线双键）|5246|
|zhiqin.switch.x103|叶绿体G1智能墙壁开关（单火线三键）|5247|
|zhj.remote.sw1e01|智和家 全域调光旋钮无线开关|37283|
|zhj.switch.k21k|智和家 K2智能开关一键|40933|
|zhj.switch.k22k|智和家 K2智能开关二键|40932|
|zhj.switch.k23k|智和家 K2智能开关三键|40931|
|zhj.switch.k24k|智和家 K2智能开关四键|40930|
|zhj.switch.k28k|智和家 K2智能开关八键|40904|
|zhj.switch.sw1a01|智和家L智能开关一开|18739|
|zhj.switch.sw1c01|智和家 K1百变智能开关 一键|27380|
|zhj.switch.sw1d02|智和家 T2单零火智能开关 一键|35847|
|zhj.switch.sw1e01|智和家 T1零火智能开关 一键|30141|
|zhj.switch.sw2a01|智和家L智能开关二开|18738|
|zhj.switch.sw2b01|智和家 K1百变智能开关 二键|27375|
|zhj.switch.sw2d02|智和家 T2单零火智能开关 二键|35848|
|zhj.switch.sw2e01|智和家 T1零火智能开关 二键|30142|
|zhj.switch.sw3a01|智和家L智能开关三开|18737|
|zhj.switch.sw3b01|智和家 K1百变智能开关 三键|27377|
|zhj.switch.sw3d02|智和家 T2单零火智能开关 三键|35849|
|zhj.switch.sw3e01|智和家 T1零火智能开关 三键|30144|
|zhj.switch.sw4a01|智和家L智能开关四开|18729|
|zhj.switch.sw4b01|智和家 K1百变智能开关 四键|27378|
|zhj.switch.sw4e01|智和家 T1零火智能开关 四键|30150|
|zhj.switch.t1max1|智和家 T1 Max智能屏显开关一键|38203|
|zhj.switch.t1max2|智和家 T1 Max智能屏显开关二键|38204|
|zhj.switch.t1max3|智和家 T1 Max智能屏显开关三键|38205|
|zhj.switch.t1pro1|智和家 T1 Pro智能开关一键|38199|
|zhj.switch.t1pro2|智和家 T1 Pro智能开关二键|38200|
|zhj.switch.t1pro3|智和家 T1 Pro智能开关三键|38201|
|zhj.switch.t1pro4|智和家 T1 Pro智能开关四键|38202|
|zhj.switch.zhjc11|智和家 C1超薄开关一键|23113|
|zhj.switch.zhjc12|智和家 C1超薄开关二键|23114|
|zhj.switch.zhjc13|智和家 C1超薄开关三键|23115|
|zhj.switch.zhjc14|智和家 C1超薄开关四键|23116|
|zhj.switch.zhjc1p|智和家C1超薄屏开关|24877|
|zhj.switch.zhjw01|智和家 超薄零火屏显开关 二开|31777|
|zhj.switch.zhjw02|智和家 超薄零火屏显开关 三开|31778|
|zhj.switch.zhjw03|智和家 超薄零火屏显开关 四开|31779|
|zhj.switch.zhjw04|智和家 超薄圆屏多功能面板|31780|
|zhzt.switch.ni2a11|NVC雷士电工 墙壁开关 Ni2（零火MESH单键）|25303|
|zhzt.switch.ni2a21|NVC雷士电工 墙壁开关 Ni2（零火MESH双键）|25304|
|zhzt.switch.ni2a31|雷士墙壁开关MESH（零火 三键）|25305|
|zhzt.switch.ni2a32|NVC 雷士电工墙壁开关 Ni2（零火MESH三键）|25920|
|zhzt.switch.nia11|NVC雷士 单火智能开关 Ni（一位）|9355|
|zhzt.switch.nia21|NVC雷士 单火智能开关 Ni（二位）|9361|
|zhzt.switch.nia31|NVC雷士 单火智能开关 Ni（三位）|9362|
|zhzt.switch.sw1a01|NVC雷士电工一位蓝牙复合开关 Q22|29767|
|zhzt.switch.sw1b01|雷士电工一位蓝牙复合开关Q19|31800|
|zhzt.switch.sw1c02|NVC雷士电工 一位零火智能开关 N26|37507|
|zhzt.switch.sw1d03|NVC雷士电工 一位零火智能开关BLE-Mesh|37596|
|zhzt.switch.sw2a01|NVC雷士电工二位蓝牙复合开关 Q22|29768|
|zhzt.switch.sw2b01|雷士电工二位蓝牙复合开关Q19|31801|
|zhzt.switch.sw2c02|NVC雷士电工 二位零火智能开关 N26|37508|
|zhzt.switch.sw2d03|NVC雷士电工 二位零火智能开关BLE-Mesh|37597|
|zhzt.switch.sw3a01|NVC雷士电工三位蓝牙复合开关 Q22|29769|
|zhzt.switch.sw3b01|雷士电工三位蓝牙复合开关Q19|31802|
|zhzt.switch.sw3c02|NVC雷士电工 三位零火智能开关 N26|37509|
|zhzt.switch.sw3d03|NVC雷士电工 三位零火智能开关BLE-Mesh|37598|
|zhzt.switch.sw4a01|NVC雷士电工 四位3路带屏蓝牙复合开关 Q22|29770|
|zhzt.switch.sw4b01|雷士电工四位蓝牙复合开关Q19|31803|
|zhzt.switch.sw6a01|NVC雷士电工四位零火智能开关BLE-Mesh|31998|
|zidt.switch.8k|ZIDT智能八键开关mesh 2.0|37193|
|zidt.switch.blsw01|ZIDT智能一键开关mesh 2.0|36900|
|zidt.switch.blsw02|ZIDT智能二键开关mesh 2.0|36901|
|zidt.switch.blsw03|ZIDT智能三键开关mesh 2.0|36902|
|zidt.switch.blsw04|ZIDT智能四键开关mesh 2.0|36903|
|zimi.plug.zncz01|小米米家智能墙壁插座|3083|
|zimi.powerstrip.v2|米家智能插线板|126|
|zimi.powerstrip.vtl_v2|米家智能插线板（虚拟）|184|
|zimi.switch.dhkg01|小米米家智能开关（单开单控）|1945|
|zimi.switch.dhkg02|小米米家智能开关（双开单控）|1946|
|zimi.switch.dhkg05|小米米家智能开关（三开单控）|5937|
|zinguo.plug.c2m|智能墙壁插座WiFi版|71599|
|zinguo.plug.sc02|智能定时器|10898|
|zinguo.switch.b3|两线浴霸开关|11218|
|zinguo.switch.b5m|智能浴霸开关|5744|
|zinguo.switch.zc1w|峥果一键开关(WIFI)|32461|
|zinguo.switch.zc2w|峥果二键开关(WIFI)|32460|
|zinguo.switch.zc3w|峥果三键开关(WIFI)|32459|
|zinguo.switch.zc4w|峥果四键开关(WIFI)|32458|
|zjaj.switch.sw1a01|VELBERT一位智能开关|29401|
|zjaj.switch.sw2a01|VELBERT二位智能开关|29402|
|zjaj.switch.sw3a01|VELBERT三位智能开关|29404|
|zjaj.switch.sw4a01|VELBERT四位智能开关|29405|
|zjcx.plug.qcsw02|传翔磁吸墙充插座|25140|
|zjcx.switch.s6|六路开关模块|4367|
|zjj.switch.sw1a01|追尖智能开关一开蓝牙Mesh2.0|39527|
|zjj.switch.sw2a01|追尖智能开关二开蓝牙Mesh2.0|39528|
|zjj.switch.sw3a01|追尖智能开关三开蓝牙Mesh2.0|39529|
|zjj.switch.sw4a01|追尖智能开关四开蓝牙Mesh2.0|39530|
|zksq.switch.sw1a01|SWAN HOME一键智能开关|28058|
|zksq.switch.sw1b01|SWAN HOME智能开关一键B1Pro|32107|
|zksq.switch.sw2a01|SWAN HOME二键智能开关|28059|
|zksq.switch.sw2b01|SWAN HOME智能开关二键B1Pro|32108|
|zksq.switch.sw3a01|SWAN HOME三键智能开关|28060|
|zksq.switch.sw3b01|SWAN HOME智能开关三键B1Pro|32109|
|zksq.switch.sw4a01|SWAN HOME四键智能开关|28061|
|zksq.switch.sw4a02|SWAN HOME四键智能带屏开关|28062|
|zlx.switch.zlxkg1|智领袖智能开关（一路）|32888|
|zlx.switch.zlxkg2|智领袖智能开关（二路）|32889|
|zlx.switch.zlxkg3|智领袖智能开关（三路）|32890|
|zlx.switch.zlxkg4|智领袖智能开关（四路）|32891|
|zlx.switch.zlxsv1|智领袖 智能开关（一开）|39961|
|zlx.switch.zlxsv2|智领袖 智能开关（二开）|39962|
|zlx.switch.zlxsv3|智领袖 智能开关（三开）|39963|
|zlx.switch.zlxsv4|智领袖 智能开关（四开）|39964|
|zlyj88.remote.ypwx1|雁派六键无线开关（BLE）|33273|
|zlyj88.switch.ypkg1|雁派智能一路开关（Mesh2.0）|31134|
|zlyj88.switch.ypkg2|雁派智能二路开关（Mesh2.0）|31135|
|zlyj88.switch.ypkg3|雁派智能三路开关（Mesh2.0）|31136|
|zlyj88.switch.ypkg4|雁派智能四路开关（Mesh2.0）|31137|
|znsn.cs.ck01|Thoughthome插卡取电器|25600|
|znsn.cs.cp01m|znsn蓝牙Mesh插卡取电开关|15440|
|znsn.switch.bln31|ZNSN一键屏显开关|24112|
|znsn.switch.bln32|ZNSN二键屏显开关|24115|
|znsn.switch.bln33|ZNSN三键屏显开关|24117|
|znsn.switch.bln34|ZNSN四键屏显开关|24118|
|znsn.switch.bln36|ZNSN六键屏显开关|24121|
|znsn.switch.g701|Thoughthome单零火线G系列一开开关|31748|
|znsn.switch.g702|Thoughthome单零火线G系列二开开关|31749|
|znsn.switch.g703|Thoughthome单零火线G系列三开开关|31750|
|znsn.switch.g704|Thoughthome单零火线G系列四开开关|31751|
|znsn.switch.g706|Thoughthome单零火线G系列六开开关|31752|
|znsn.switch.g7lh01|Thoughthome零火线G系列一开开关|31753|
|znsn.switch.g7lh02|Thoughthome零火线G系列二开开关|31754|
|znsn.switch.g7lh03|Thoughthome零火线G系列三开开关|31755|
|znsn.switch.g7lh04|Thoughthome零火线G系列四开开关|31757|
|znsn.switch.g7lh06|Thoughthome零火线G系列六开开关|31758|
|znsn.switch.oled1|znsn半屏Mesh单键开关|16865|
|znsn.switch.oled2|znsn半屏Mesh双键开关|16864|
|znsn.switch.oled3|znsn半屏Mesh三键开关|16863|
|znsn.switch.oled4|znsn半屏Mesh四键开关|16862|
|znsn.switch.oled6|znsn半屏Mesh六键开关|16854|
|znsn.switch.tdq1a|znsn蓝牙通断器|15839|
|znsn.switch.yjpd1|ZNSN正尚一键开关|20924|
|znsn.switch.yjpd2|ZNSN正尚二键开关|20925|
|znsn.switch.yjpd3|ZNSN正尚三键开关|20926|
|znsn.switch.yjpd4|ZNSN正尚四键开关|20674|
|znsn.switch.z1g3|znsn蓝牙Mesh单键开关2.0|20842|
|znsn.switch.z2g3|znsn蓝牙Mesh双键开关2.0|20841|
|znsn.switch.z3g3|znsn蓝牙Mesh三键开关2.0|20840|
|znsn.switch.z4g3|znsn蓝牙Mesh四键开关2.0|20839|
|znsn.switch.zg1m|znsn蓝牙Mesh单键开关(零火)|12054|
|znsn.switch.zg1ml|znsn蓝牙Mesh单键开关(单火)|12061|
|znsn.switch.zg2m|znsn蓝牙Mesh双键开关(零火)|12055|
|znsn.switch.zg2ml|znsn蓝牙Mesh双键开关(单火)|12062|
|znsn.switch.zg3m|znsn蓝牙Mesh三键开关(零火)|12058|
|znsn.switch.zg3ml|znsn蓝牙Mesh三键开关(单火)|12063|
|znsn.switch.zg4m|znsn蓝牙Mesh四键开关(零火)|12059|
|znsn.switch.zg4ml|znsn蓝牙Mesh四键开关(单火)|12064|
|znsn.switch.zg8m|znsn蓝牙Mesh八键开关(零火)|12060|
|znsn.switch.zg8ml|znsn蓝牙Mesh八键开关(单火)|12065|
|znsn.switch.zm1a|znsn蓝牙Mesh开关单键（零火）|8250|
|znsn.switch.zm1d|znsn蓝牙Mesh开关单键（单火）|8253|
|znsn.switch.zm2a|znsn蓝牙Mesh开关双键（零火）|8251|
|znsn.switch.zm2d|znsn蓝牙Mesh开关双键（单火）|8254|
|znsn.switch.zm3a|znsn蓝牙Mesh开关三键（零火）|8252|
|znsn.switch.zm3d|znsn蓝牙Mesh开关三键（单火）|8255|
|znsn.switch.zs1w|Thoughthome G7款零火版WIFI一键开关|32457|
|znsn.switch.zs2w|Thoughthome G7款零火版WIFI二键开关|32456|
|znsn.switch.zs3w|Thoughthome G7款零火版WIFI三键开关|32455|
|znsn.switch.zs4w|Thoughthome G7款零火版WIFI四键开关|32454|
|zqdq.switch.sw1a01|志高智能一键开关|36798|
|zqdq.switch.sw1b01|志高智联一键开关|36802|
|zqdq.switch.sw2a01|志高智能二键开关|36799|
|zqdq.switch.sw2b01|志高智联二键开关|36803|
|zqdq.switch.sw3a01|志高智能三键开关|36800|
|zqdq.switch.sw3b01|志高智联三键开关|36804|
|zqdq.switch.sw4a01|志高智能四键开关|36801|
|zqdq.switch.sw4b01|志高智联四键开关|36805|
|zqdq.switch.sxpx01|志高一键屏显开关|36559|
|zqdq.switch.sxpx02|志高二键屏显开关|36560|
|zqdq.switch.sxpx03|志高三键屏显开关|36561|
|zqm4g.switch.tdq02|ZQM浙旗明通断器WiFi版|29474|
|zuka.switch.sw1a01|佐卡智能 一键开关2.0|25650|
|zuka.switch.sw2a01|佐卡智能 二键开关2.0|25651|
|zuka.switch.sw3a01|佐卡智能 三键开关2.0|25652|
|zuka.switch.sw4a01|佐卡智能 四键开关2.0|25653|
|zxd123.plug.jdls1|Sparkleiot智能插座|35385|
|zxd123.switch.xhtdq|Sparkleiot智能通断器|37806|
|zxlink.switch.zxltd2|智相连通断器|38745|
|zxlink.switch.zxltdq|智相连Mesh2.0通断器|35553|
|zyzy1.plug.y07012|空调插座|73541|
|zzljzn.switch.px01|智无愚屏显一键开关|35271|
|zzljzn.switch.px02|智无愚屏显二键开关|35272|
|zzljzn.switch.px03|智无愚屏显三键开关|35273|
|zzljzn.switch.sw1a01|智无愚智能开关一键|32540|
|zzljzn.switch.sw2a01|智无愚智能开关二键|32541|
|zzljzn.switch.sw3a01|智无愚智能开关三键|32542|
|zzljzn.switch.sw4a01|智无愚智能开关四键|34200|
|zzslc.switch.slw06|松联诚屏显开关S7二开|31073|
|zzslc.switch.slw12|松联诚超薄开关S5一开|31297|
|zzslc.switch.slw13|松联诚超薄开关S5二开|31394|
|zzslc.switch.slw14|松联诚超薄开关S5三开|31400|
|zzslc.switch.slw15|松联诚超薄开关S5四开|31407|
|zzslc.switch.slw16|松联诚屏显开关S7一开|31415|
|zzslc.switch.slw17|松联诚屏显开关S7三开|31416|
|zzslc.switch.slw18|松联诚屏显开关S7四开|31417|
|zzslc.switch.slw19|松联诚圆屏多功能开关|31613|
|zzslc.switch.slw20|松联诚全面屏多功能开关|31620|
|zzw.switch.sw1a01|智己人智能开关零火版（单开）|28866|
|zzw.switch.sw1c02|智己人一键开关（M10）零火版|34038|
|zzw.switch.sw2a01|智己人智能开关零火版（双开）|28867|
|zzw.switch.sw2c01|智己人二键开关（M10）零火版|34030|
|zzw.switch.sw3a01|智己人智能开关零火版（三开）|28871|
|zzw.switch.sw3c01|智己人三键开关（M10）零火版|34031|
|zzw.switch.sw4a01|智己人智能开关零火版（四开）|28872|
|zzw.switch.sw4b01|智己人四键开关(M11)零火版|34028|
|zzw.switch.sw4c01|智己人四键开关（M10）零火版|34033|
|zzx.switch.px1|简智宅一键屏显开关|30145|
|zzx.switch.px2|简智宅二键屏显开关|30146|
|zzx.switch.px3|简智宅三键屏显开关|30147|
|zzx.switch.px4|简智宅四键屏显开关|30148|

### 清洁电器

|model|name|pd_id|
|---|---|---:|
|aupu.airer.d350m|奥普晾衣架D350M|28849|
|aupu.airer.l8m|奥普晾衣架L8M|28394|
|babai.airer.hc01b|黑创 智能晾衣架 s63|4231|
|babai.airer.lyj01|Ai 智能晾衣架|68901|
|bangbo.airer.c3xhqm|彩魅智能晾衣机|3885|
|bangbo.airer.x3xhqm|贝纳森X3|3368|
|bangbo.airer.x5xhqm|黑创智能晾衣机|4153|
|bangbo.airer.y6|曼斯库博Y款|3065|
|beihao.airer.airer3|向阳智能电动晾衣架|2740|
|beihao.airer.bd|蓝柚智能晾衣架|3728|
|beihao.airer.l9|丽升电动晾衣机|3726|
|beihao.airer.l9xf|佳爵士电动晾衣架|3757|
|beihao.airer.lyj08|Ai 智能晾衣机|3329|
|bshcn.dry.2j7x10|西门子iQ300干衣机|84082|
|bshcn.dry.52000w|博世4系干衣机|83569|
|bshcn.dry.52010w|博世4系干衣机|83566|
|bshcn.dry.52080w|博世4系干衣机|83574|
|bshcn.dry.52j7x8|西门子iQ300干衣机|84080|
|bshcn.dry.52u00w|博世摩德纳干衣机|83575|
|bshcn.dry.52u10w|博世摩德纳干衣机|83579|
|bshcn.dry.52u20w|博世4系干衣机|84077|
|bshcn.dry.52u60w|博世摩德纳干衣机|83573|
|bshcn.dry.52u80w|博世摩德纳干衣机|83675|
|bshcn.dry.52y01w|博世4系干衣机|84084|
|bshcn.dry.52y10w|博世4系干衣机|84810|
|bshcn.dry.52y11w|博世4系干衣机|84083|
|bshcn.dry.552u00|博世4系干衣机|83851|
|bshcn.dry.552y01|博世4系干衣机|84085|
|bshcn.dry.55d00w|博世6系干衣机|83270|
|bshcn.dry.55d10w|博世6系干衣机|83268|
|bshcn.dry.55u00w|博世6系干衣机|83113|
|bshcn.dry.55u01w|博世6系干衣机|84815|
|bshcn.dry.55u10w|博世摩德纳干衣机|83457|
|bshcn.dry.55u20w|博世大师干衣机|83561|
|bshcn.dry.55u50w|博世大师干衣机|83564|
|bshcn.dry.55u51w|博世6系干衣机|84813|
|bshcn.dry.55u60w|博世摩德纳干衣机|83461|
|bshcn.dry.55u80w|博世摩德纳干衣机|83458|
|bshcn.dry.55y10w|博世6系干衣机|84811|
|bshcn.dry.56c00w|博世8系进口干衣机|84390|
|bshcn.dry.755u00|博世大师干衣机|83565|
|bshcn.dry.755u60|博世大师干衣机|83563|
|bshcn.dry.75601w|博世干衣机|83455|
|bshcn.dry.76h80w|博世6系干衣机|83267|
|bshcn.dry.79h00w|博世6系干衣机|83264|
|bshcn.dry.b2c00w|西门子iQ700干衣机|84249|
|bshcn.dry.c3c10w|西门子iQ500干衣机|83142|
|bshcn.dry.c3c80w|西门子iQ500干衣机|83143|
|bshcn.dry.c3d10w|西门子iQ500干衣机|83103|
|bshcn.dry.c3d80w|西门子iQ500干衣机|83144|
|bshcn.dry.d7u10w|西门子iQ500干衣机|84745|
|bshcn.dry.d7u20w|西门子iQ500干衣机|84744|
|bshcn.dry.f7u20w|西门子包豪斯干衣机|83578|
|bshcn.dry.j5000w|西门子iQ300干衣机|83567|
|bshcn.dry.j5080w|西门子iQ300干衣机|83576|
|bshcn.dry.j7u00w|西门子小幸熨干衣机|83571|
|bshcn.dry.j7u10w|西门子小幸熨干衣机|83570|
|bshcn.dry.j7u29w|西门子小幸熨干衣机|83572|
|bshcn.dry.j7u70w|西门子小幸熨干衣机|83577|
|bshcn.dry.j7u80w|西门子小幸熨干衣机|83568|
|bshcn.dry.j7x00w|西门子小幸熨干衣机|83681|
|bshcn.dry.j7x10w|西门子小幸熨干衣机|83676|
|bshcn.dry.j7x80w|西门子小幸熨干衣机|83677|
|bshcn.dry.j7y01w|西门子iQ300干衣机|84078|
|bshcn.dry.j7y11w|西门子iQ300干衣机|84081|
|bshcn.dry.j7y81w|西门子iQ300干衣机|84079|
|bshcn.dry.k7u00w|西门子iQ500干衣机|83141|
|bshcn.dry.k7u10w|西门子iQ500热泵干衣机|82161|
|bshcn.dry.k7u29w|西门子小幸熨干衣机|83459|
|bshcn.dry.k7u70w|西门子小幸熨干衣机|83460|
|bshcn.dry.k7u80w|西门子小幸熨干衣机|83456|
|bshcn.dry.m7u10w|西门子包豪斯干衣机|83560|
|bshcn.dry.m7u20w|西门子包豪斯干衣机|83559|
|bshcn.dry.m7u29w|西门子iQ500干衣机|84812|
|bshcn.dry.m7u71w|西门子iQ500干衣机|84814|
|bshcn.dry.m7u80w|西门子包豪斯干衣机|83562|
|bshcn.dry.u6h00w|西门子iQ500干衣机|83266|
|bshcn.dry.u6h80w|西门子iQ500干衣机|83265|
|bshcn.washer.0au00w|博世壁挂式迷你洗衣机|84251|
|bshcn.washer.2j5000|西门子iQ300洗干一体机|83689|
|bshcn.washer.2j5080|西门子iQ300洗干一体机|83685|
|bshcn.washer.2j7i00|西门子iQ300洗干一体机|83690|
|bshcn.washer.2j7i10|西门子iQ300洗干一体机|83694|
|bshcn.washer.2j7i80|西门子iQ300洗干一体机|83695|
|bshcn.washer.4d3a10|西门子iQ500洗干一体机12kg|83224|
|bshcn.washer.4j7i10|西门子iQ300洗衣机|84646|
|bshcn.washer.52000w|博世4系洗衣机|83537|
|bshcn.washer.52010w|博世4系洗衣机|83533|
|bshcn.washer.52080w|博世4系洗衣机|83539|
|bshcn.washer.52i00w|博世4系洗干一体机|83697|
|bshcn.washer.52i10w|博世4系洗衣机|84847|
|bshcn.washer.52j7i8|西门子iQ300洗衣机|84064|
|bshcn.washer.52j7y0|西门子iQ300洗衣机|84063|
|bshcn.washer.52j7y1|西门子iQ300洗衣机|84065|
|bshcn.washer.52y00w|博世摩德纳洗衣机|83550|
|bshcn.washer.52y10w|博世摩德纳洗衣机|83549|
|bshcn.washer.52y60w|博世摩德纳洗衣机|83545|
|bshcn.washer.52y80w|博世摩德纳洗衣机|83554|
|bshcn.washer.54b01w|博世6系洗衣机|83255|
|bshcn.washer.54b0hw|博世6系洗衣机|83260|
|bshcn.washer.54b8hw|博世6系洗衣机|83256|
|bshcn.washer.54b9hw|博世6系洗衣机|83259|
|bshcn.washer.54c00w|博世6系洗衣机|83261|
|bshcn.washer.54c10w|博世6系洗衣机|83257|
|bshcn.washer.54c31w|博世8系洗衣机|84253|
|bshcn.washer.54d00w|博世摩德纳洗衣机|83112|
|bshcn.washer.54d01w|博世6系洗衣机|84807|
|bshcn.washer.54d10w|博世摩德纳洗衣机|83449|
|bshcn.washer.54d20w|博世大师洗衣机|83526|
|bshcn.washer.54d50w|博世大师洗衣机|83528|
|bshcn.washer.54d51w|博世6系洗衣机|84805|
|bshcn.washer.54d60w|博世摩德纳洗衣机|83452|
|bshcn.washer.54d80w|博世摩德纳洗衣机|83450|
|bshcn.washer.54f20w|博世4系洗衣机|84059|
|bshcn.washer.54g10w|博世6系洗干一体机|83686|
|bshcn.washer.552y00|博世4系洗衣机|83849|
|bshcn.washer.56b00w|博世8系进口洗衣机|84392|
|bshcn.washer.56g20w|博世6系洗干一体机|84067|
|bshcn.washer.74d20w|博世8系洗衣机|84743|
|bshcn.washer.74f80w|博世6系洗衣机|84647|
|bshcn.washer.752y00|博世4系洗衣机|84061|
|bshcn.washer.752y10|博世4系洗衣机|84060|
|bshcn.washer.754d00|博世大师洗衣机|83529|
|bshcn.washer.754d60|博世大师洗衣机|83530|
|bshcn.washer.8560hw|博世6系洗衣机|83258|
|bshcn.washer.a6b00w|西门子iQ800洗衣机|83444|
|bshcn.washer.b2b00w|西门子iQ700进口洗衣机|84391|
|bshcn.washer.c2b0hw|西门子iQ500洗衣机|83254|
|bshcn.washer.c3b8hw|西门子iQ500洗衣机|83252|
|bshcn.washer.c5a10w|西门子iQ500洗干一体机|83425|
|bshcn.washer.c5c10w|西门子iQ500洗衣机|83098|
|bshcn.washer.c5c80w|西门子iQ500洗衣机|83139|
|bshcn.washer.c8c11w|西门子iQ700洗衣机|84252|
|bshcn.washer.d3b10w|西门子iQ500洗衣机|83445|
|bshcn.washer.f7f20w|西门子包豪斯洗衣机|83531|
|bshcn.washer.j5000w|西门子iQ300洗衣机|83534|
|bshcn.washer.j5080w|西门子iQ300洗衣机|83535|
|bshcn.washer.j552y0|博世4系洗衣机|84062|
|bshcn.washer.j7a10w|西门子小幸熨洗衣机|83548|
|bshcn.washer.j7a80w|西门子小幸熨洗衣机|83552|
|bshcn.washer.j7i00w|西门子小幸熨洗衣机|83543|
|bshcn.washer.j7i10w|西门子小幸熨洗衣机|83542|
|bshcn.washer.j7i80w|西门子小幸熨洗衣机|83553|
|bshcn.washer.j7y00w|西门子小幸熨洗衣机|83540|
|bshcn.washer.j7y10w|西门子小幸熨洗衣机|83546|
|bshcn.washer.j7y70w|西门子小幸熨洗衣机|83547|
|bshcn.washer.j7y81w|西门子小幸熨洗衣机|83551|
|bshcn.washer.k7d00w|西门子小幸熨洗衣机|83140|
|bshcn.washer.k7d10w|西门子iQ500超氧洗衣机|82160|
|bshcn.washer.k7d11w|西门子iQ500洗衣机|84254|
|bshcn.washer.k7d29w|西门子小幸熨洗衣机|83451|
|bshcn.washer.k7d70w|西门子小幸熨洗衣机|83453|
|bshcn.washer.k7d80w|西门子小幸熨洗衣机|83448|
|bshcn.washer.k7g00w|西门子iQ500洗干一体机|83701|
|bshcn.washer.k7g10w|西门子iQ500洗干一体机|83603|
|bshcn.washer.k7g80w|西门子iQ500洗干一体机|83687|
|bshcn.washer.m7d10w|西门子包豪斯洗衣机|83525|
|bshcn.washer.m7d20w|西门子包豪斯洗衣机|83454|
|bshcn.washer.m7d29w|西门子iQ500洗衣机|84804|
|bshcn.washer.m7d71w|西门子iQ500洗衣机|84806|
|bshcn.washer.m7d80w|西门子包豪斯洗衣机|83527|
|bshcn.washer.m7g20w|西门子iQ500洗干一体机|84066|
|bshcn.washer.p5y70w|西门子iQ300洗衣机|84854|
|bshcn.washer.p752y1|博世4系洗衣机|84803|
|bshcn.washer.p7d20w|西门子iQ700洗衣机|84648|
|bshcn.washer.u561hw|西门子iQ500洗衣机|83263|
|bshcn.washer.u5x8hw|西门子iQ500洗干一体机|83298|
|bshcn.washer.u7b1hw|西门子iQ500洗衣机|83253|
|bshcn.washer.w6600w|西门子iQ800洗衣机|83447|
|bshcn.washer.w7010w|西门子壁挂式迷你洗衣机|83481|
|bshcn.washer.ws52j7|西门子iQ300洗干一体机|84845|
|cchip.airer.a2|曼斯库博P系列|3964|
|czjx.airer.a7|芝森晾衣架|38281|
|czqh.airer.jsw2|卡瑞琪COURAGE智能电动晾衣机M9|34562|
|czqh.airer.krqjsw|卡瑞琪COURAGE一线天智能晾衣架|34524|
|czqh.airer.krqlyj|卡瑞琪COURAGE单功能晾衣架（HZ）|30642|
|czqh.airer.yxtlyj|卡瑞琪COURAGE一线天晾衣架|32258|
|dji.vacuum.romo|DJI ROMO|80925|
|dooya.airer.2m|杜亚智能晾衣机2M|32722|
|dooya.airer.mjlyj|盼盼智能晾衣机|68312|
|dreame.vacuum.ma1808|米家扫拖机器人1C|72473|
|dreame.vacuum.mc1808|米家扫拖机器人1C|66181|
|dreame.vacuum.p2028|追觅Z10 Pro|72190|
|dreame.vacuum.p2140|米家扫拖机器人2C|71742|
|e11035.airer.1208a|黑创HRLCHURE智能晾衣架|7070|
|e11035.airer.1208b|LFK智能晾衣机|7071|
|e11035.airer.9000x|太太乐TES款单功能晾衣机|6129|
|e11035.airer.9003sx|太太乐TES款全功能晾衣机|4981|
|e11035.airer.a6|九牧A6090电动晾衣机|6520|
|e11035.airer.t10l|JL单功能智能晾衣机|6519|
|e11035.airer.t10xfh|JL全功能智能晾衣机|6518|
|eco.vacuum.dibao|科沃斯扫地机器人|84726|
|eco.vacuum.tveglj|DEEBOT N50|82350|
|gdyimu.vacuum.g1m|Lydsto惯导扫拖机器人G1M|5961|
|gdyimu.vacuum.r1|Lydsto扫拖一体机R1A|72192|
|gdyimu.vacuum.r1da|Lydsto智能扫拖机器人R1DA|73349|
|giot.airer.v1icdw|V1智能晾衣架（WiFi）|15699|
|giot.airer.v2icdw|V2智能晾衣架（WiFi）|17529|
|gofull.airer.gflyj|格峰真隐藏晾衣机|30920|
|gszn.airer.gs1685|金贵夫人晾衣架|12878|
|gszn.airer.gs1686|GS智能晾衣架|13146|
|haikuo.cleaner.m7|无线吸尘器|13106|
|hanyi.vacuum.m7pro|美倾互联网智能扫地机器人|71708|
|hanyi.vacuum.m8pro|美倾M8互联网智能扫地机器人|74720|
|horow.airer.p90|希箭智能晾衣机|5660|
|hotata.airer.d10zm|好太太晾衣机D10-ZM|25421|
|hotata.airer.d3063|好太太晾衣机D-3063(M13)|23300|
|hotata.airer.d3115|好太太晾衣机D-3115S|3600|
|hotata.airer.d3375|好太太晾衣机D-3375|23299|
|hotata.airer.q30pzm|好太太晾衣机Q30Plus-ZM|25805|
|hotata.airer.q31zm|好太太晾衣机Q31-ZM|25789|
|hotata.airer.q60zm|好太太晾衣机Q60-ZM|25804|
|hyd.airer.1s|米家智能晾衣机 1S|11326|
|hyd.airer.cs|好易点智能晾衣机GEN|9620|
|hyd.airer.gen|邦先生智能晾衣机GEN|11128|
|hyd.airer.gen2|邦先生智能晾衣机GEN|13494|
|hyd.airer.gen3|邦先生智能晾衣机GEN 2|24329|
|hyd.airer.gen4|邦先生智能晾衣机GEN 3|31786|
|hyd.airer.h51a|好易点智能晾衣机-简约款2|5529|
|hyd.airer.h51c|好易点智能晾衣机-消毒款2|5530|
|hyd.airer.hx1|好易点智能晾衣机HX1|3156|
|hyd.airer.hx2|好易点智能晾衣机HX2|3533|
|hyd.airer.hx3|好易点智能晾衣机HX3|3157|
|hyd.airer.l22pro|邦先生智能晾衣机 双控款|31060|
|hyd.airer.m36a|智能晾衣机-双机款|8216|
|hyd.airer.pro2|米家智能晾衣机Pro|13832|
|hyd.airer.znlyj1|米家智能晾衣机|1820|
|hyd.airer.znlyj2|米家智能晾衣机|5206|
|hyd.airer.znlyj3|米家智能晾衣机|5501|
|hyd.airer.znlyj4|米家智能晾衣机|5805|
|ijomoo.airer.a1060h|九牧智能晾衣机A1060H|29456|
|ijomoo.airer.mja6|九牧智能晾衣机-A6090|7019|
|iot.vacuum.cc1|ZN-智能擦窗机器人|20827|
|jdjz.airer.a3max|京东京造 A3Max智能晾衣架|37861|
|jdjz.airer.a3pro|京东京造A3Max 智能晾衣机|26626|
|jdjz.airer.jdlyj|京东京造隐形单杆智能晾衣机|31697|
|jdjz.airer.jza08|京东京造智能双控晾衣机|32349|
|jdjz.airer.v1|京东京造智能晾衣机A5 Pro|38298|
|jdyw.vacuum.t300|友望扫地机器人T300|81745|
|jdyw.vacuum.u300p|友望扫地机器人U300|80719|
|jdyw.vacuum.u400|友望扫地机器人U400|82918|
|jdyw.vacuum.u400m|友望扫地机器人U400 Max|84732|
|jgfr.airer.yxtlyj|金贵夫人隐形晾衣架|33656|
|jgfr.airer.znlyj|金贵夫人智能晾衣架|30539|
|jielan.airer.ycs|杰兰特电动晾衣架01|38476|
|jldj.airer.80036h|H智能晾衣架|9470|
|jnms15.airer.1|太太夸智能晾衣架|31007|
|jns.airer.1|捷纳森智能晾衣架|7430|
|joybos.airer.jbslyj|佳帮手智能电动晾衣架|11551|
|jxdh.dry.zx002|大豪智芯宠物烘干机1号Pro|19723|
|jxdh.dry.zxcw02|大豪智芯宠物烘干机Mini一号|26260|
|kaadas.airer.km01|凯迪仕基础晾衣机|5607|
|kejia.airer.jjs|佳爵士智能晾衣机|71179|
|kejia.airer.krq|Courage智能晾衣机|71178|
|kejia.airer.krqpro|Courage智能晾衣机PRO|4316|
|kejia.airer.mzn|米智能·电动晾衣机|70067|
|kejia.airer.mznpro|米智能·电动晾衣机PRO|4459|
|kejia.airer.th001|金贵夫人智能晾衣机|66493|
|kejia.airer.yzjpro|伊智佳智能晾衣机PRO|5157|
|kingee.airer.kelyj5|博高科智能电动晾衣机|4405|
|koey.airer.wy0a04|KOEY智能晾衣架|16905|
|ksks.airer.pro|今上智能晾衣机Pro|29047|
|kxf321.mop.mo001|钟点狗智能擦地机|65615|
|kxf321.mop.mo002|钟点狗智能擦地机S|2276|
|lbest.airer.lm01|晾霸智能晾衣机|1569|
|lbest.airer.lm04|晾霸晾衣机S31|35863|
|lbest.airer.lm05|晾霸智能晾衣机S32|36350|
|lbest.airer.lm07|晾霸智能晾衣机D11|37705|
|lbest.airer.lm08|晾霸智能晾衣机PRO|38119|
|lbest.airer.lm09|晾霸智能晾衣机SE|38120|
|leishi.airer.lyj001|雷士智能晾衣架PRO|5081|
|leishi.airer.lyj002|雷士智能晾衣架|5608|
|lge.dry.dryer|LG干衣机|83092|
|lge.washer.washer|LG全自动滚筒洗衣机|83100|
|lzkj.airer.lylyj|绿智晾衣架|32400|
|mibx2.washer.v1|米家互联网直驱洗烘一体机 10kg|2764|
|mibx2.washer.v11|米家直驱洗烘一体机 10kg|9381|
|mibx2.washer.v13|米家Mini洗衣机 1kg|10402|
|mibx2.washer.v15rm|米家洗烘一体机 12kg/11.8kg 钛金灰|13456|
|mibx2.washer.v2|米家直驱洗烘一体机 10kg|4466|
|mibx2.washer.v3|米家波轮洗衣机 10kg|4499|
|mibx2.washer.v7|直驱｜米家洗烘一体机 尊享版10kg|6536|
|mibx5.dry.v6|米家干衣机 10kg|13258|
|mibx5.washer.32|米家洗衣机 ｜ 超净洗 滚筒10kg|15732|
|mibx5.washer.35|米家洗衣机 超净洗 洗烘10kg|15733|
|mibx5.washer.f52|米家洗衣机 洗烘12kg|25871|
|mibx5.washer.f521|米家洗衣机 洗烘12kg|26807|
|mibx5.washer.f56|米家洗衣机Pro 蓝氧 洗烘10kg|24378|
|mibx5.washer.f60|米家洗衣机Pro 蓝氧 洗烘12kg|25872|
|mibx5.washer.f69|米家洗衣机Pro 超电解智投 滚筒12kg|28149|
|mibx5.washer.f81|米家洗衣机 滚筒12kg|30334|
|mibx5.washer.f91|米家洗衣机 滚筒12kg|33884|
|mibx5.washer.s06|米家洗衣机Pro 迷你3kg|19597|
|mibx5.washer.s12|米家洗衣机Pro 智投 迷你3kg|24529|
|mibx5.washer.v14|直驱 / 米家滚筒洗衣机 10kg|14643|
|mibx5.washer.v4|直驱 / 米家滚筒洗衣机 尊享版 10kg|5290|
|mibx5.washer.x061|米家双区洗衣机 滚筒10kg|31160|
|micoe.airer.hz001h|四季沐歌  Mies 10  Pro-烘干款|68974|
|micoe.airer.hz001z|四季沐歌  Mies 10S 照明款|68975|
|micoe.airer.hz002h|Rise10 Mix-环形極固杆（烘干旗舰款）|69984|
|micoe.airer.hz002x|Rise10-环形極固杆（除菌&体感灯）|69983|
|micoe.airer.hz003h|四季沐歌  银河系列003(烘干款)|71233|
|micoe.airer.hz003z|四季沐歌  银河系列003(照明款)|71230|
|midjd4.washer.s08|米家洗衣机 迷你洗 洗烘|20414|
|midjd8.washer.42|米家洗衣机 超净洗Pro 洗烘12kg|16065|
|midjd8.washer.44|米家洗衣机 ｜ 超净洗Pro 洗烘一体10kg|16023|
|miele.dry.w001|美诺干衣机|83073|
|miele.washer.w001|美诺洗衣机|83071|
|mijia.vacuum.b108zb|米家扫拖机器人3S|13068|
|minij.washer.v1|小吉智能迷你滚筒洗衣机|165|
|minij.washer.v12|小吉智能水珠壁挂洗衣机|1299|
|minij.washer.v15|小吉智能迷你滚筒洗衣机2.8kg|1345|
|minij.washer.v17|小吉智能壁挂洗烘一体机|1927|
|minij.washer.v27|米家互联网迷你波轮洗衣机Pro 3kg|8600|
|moyu.washer.dg02|摩鱼内衣洗护机dg02|17161|
|moyu.washer.dg08|摩鱼内衣洗护机dg08|17162|
|moyu.washer.s1hm|摩鱼智能母婴洗衣机|65627|
|mrbond.airer.c1x|邦先生智能晾衣机-消毒款|2696|
|mrbond.airer.m0|邦先生M0智能晾衣机|1159|
|mrbond.airer.m1pro|邦先生M1pro智能晾衣机|870|
|mrbond.airer.m1s|邦先生M1智能晾衣机|892|
|mrbond.airer.m1super|邦先生M1super智能晾衣机|1026|
|mrbond.airer.m1t|邦先生智能晾衣机-简约款|2649|
|mrbond.airer.m1tpro|邦先生智能晾衣机-烘干款|2695|
|mrbond.airer.m2|邦先生M2智能晾衣机|1685|
|mrbond.airer.m2pro|邦先生M2pro智能晾衣机|1883|
|mrbond.airer.m31a|邦先生智能晾衣机-简约款2|3771|
|mrbond.airer.m31a2|邦先生智能晾衣机-简约款2|5643|
|mrbond.airer.m31c|邦先生智能晾衣机-消毒款2|3769|
|mrbond.airer.m31c2|邦先生智能晾衣机-消毒款2|5644|
|mrbond.airer.m33a|邦先生智能晾衣机-简约款3|4327|
|mrbond.airer.m33c|邦先生智能晾衣机-消毒款3|4333|
|mrbond.airer.m50f|邦先生智能晾衣机LA|6902|
|mrbond.airer.m53c|邦先生智能晾衣机-风干款|4308|
|mrbond.airer.m53cpr|邦先生智能晾衣机LDAH|6906|
|mrbond.airer.m53pro|邦先生智能晾衣机-风烘款|4309|
|mrbond.airer.m65|邦先生智能晾衣机-风烘款Pro|6097|
|mskub.airer.k6|曼斯库博K款智能晾衣机|3564|
|narwa.vacuum.001|云鲸逍遥系列 001|81646|
|narwa.vacuum.ax11|云鲸逍遥系列 002（超薄全能基站版）|82028|
|narwa.vacuum.ax12|云鲸逍遥系列 002|82029|
|narwa.vacuum.ax17|云鲸智能扫拖一体机器人 J5 pure|82041|
|narwa.vacuum.ax17p|云鲸智能扫拖一体机器人 J5经典款|84271|
|narwa.vacuum.ax18|云鲸智能扫拖一体机器人 J5Max|82036|
|narwa.vacuum.ax19|云鲸智能扫拖一体机器人 J5Max(超薄基站版)|82037|
|narwa.vacuum.ax24|云鲸活水履带洗地机器人 J6|82810|
|narwa.vacuum.ax25|云鲸活水履带洗地机器人 J6（超薄基站）|82811|
|narwa.vacuum.cx2|云鲸逍遥系列 002 Max|82018|
|narwa.vacuum.cx3mi|云鲸逍遥系列 001（轻集尘版）|81647|
|narwa.vacuum.cx3p|云鲸逍遥全智能清洁机器人 001 Pure|81367|
|narwa.vacuum.cx4|云鲸逍遥全智能清洁机器人 001 Max|81316|
|narwa.vacuum.cx7|云鲸逍遥系列 002 Max（超薄基站版）|82027|
|narwa.vacuum.j4lmi|云鲸智能扫拖一体机器人 J4Lite|81648|
|narwa.vacuum.j4mi|云鲸 J4|80780|
|narwa.vacuum.j4pmi|云鲸智能拖扫一体机器人 J4增强版|81330|
|narwa.vacuum.j5|云鲸 J5|81644|
|narwa.vacuum.j5c|云鲸智能扫拖一体机器人 J5C|82808|
|narwa.vacuum.j5x|云鲸 J5X|81645|
|narwa.vacuum.j64|云鲸活水履带洗地机器人 JX|83818|
|narwa.vacuum.j64p|云鲸 活水履带洗地机器人 JX Pro|84766|
|narwa.vacuum.j65|云鲸活水履带洗地机器人 JX（超薄基站）|83819|
|narwa.vacuum.j72|云鲸 活水履带洗地机器人 JX Ultra|84620|
|narwa.vacuum.j78|云鲸 活水履带洗地机器人 JX Ultra Plus|84621|
|narwa.vacuum.r37|云鲸 活水履带洗地机器人 J6经典版|84683|
|narwa.vacuum.x30|云鲸AI活水履带洗地机器人 逍遥003|83820|
|narwa.vacuum.x31|云鲸AI活水履带洗地机器人 逍遥003（超薄基站版）|83821|
|narwa.vacuum.x38|云鲸 AI活水履带洗地机器人 逍遥003 Ultra|84682|
|nbczwl.airer.airer|金贵夫人XM|69328|
|nbczwl.airer.kfe01|凯夫尔KFE|70458|
|nbczwl.airer.krqu40|卡瑞琪智能晾衣架|9518|
|nbczwl.airer.wtt001|WTT智能晾衣架|73786|
|nbczwl.airer.zbs01|智帮手电动晾衣架|72090|
|nbps.airer.pro|派颂智能晾衣架Pro|23331|
|novo.airer.g30|NOVO智能电动晾衣架豪华款|5253|
|novo.airer.g31|NOVO智能电动晾衣架基础款|5597|
|onej.vacuum.clean|信社真湿擦智能擦窗机YW703|16857|
|opple.airer.3022wi|OPPLE智能晾衣机  Mode A|10516|
|opple.airer.3032wi|OPPLE智能晾衣机  Mode B|10515|
|opple.airer.lyjb02|OPPLE智能晾衣机 MODEL E|26910|
|orlant.airer.b|欧兰特智能晾衣架B系列|7337|
|orlant.airer.c|欧兰特智能晾衣架C系列|5013|
|ouchen.airer.m01|智能晾衣机momo|5760|
|panpan.airer.lyj01|盼盼智能晾衣机YC系列|38501|
|panpan.airer.y18|盼盼Y18智能晾衣机|5322|
|pgkj.dry.300pzr|荣事达智能衣物护理机|9278|
|renx.airer.dilai|莱迪智能晾衣机|8566|
|renx.airer.pinsh|PISN智能晾衣架|8568|
|roborock.vacuum.a01|石头扫地机器人 E4|67932|
|roidmi.cleaner.f8pro|睿米无线吸尘器F8 Pro|2508|
|roidmi.cleaner.v1|睿米无线吸尘器 NEX S|1108|
|roidmi.cleaner.v2|睿米无线吸尘器 NEX VX|1784|
|roidmi.cleaner.v382|睿米无线吸尘器 NEX2 Pro|2145|
|roidmi.cleaner.v58|睿米无线吸尘器旗舰版|4879|
|roidmi.mop.xdj01|睿米无界超净洗地机 NEO|5711|
|roidmi.mop.xdj03|睿米无界超净洗地机R100|9504|
|roidmi.vacuum.r1b|睿米扫拖机器人EVE|73690|
|roidmi.vacuum.sdj60|ROIDMI EVE MAX|11223|
|roidmi.vacuum.v1|ROIDMI手持无线吸尘器|584|
|roidmi.vacuum.v60|睿米扫拖机器人EVE|69844|
|roidmi.vacuum.v62|ROIDMI EVE CC|78053|
|roidmi.vacuum.v66|睿米真全能扫拖机器人|72592|
|sfy.airer.l001|索菲亚智能晾衣架M1|24061|
|sfy.airer.l002|索菲亚智能晾衣架M1|23760|
|sfy.airer.l003|索菲亚智能隐形晾衣架M2|34951|
|sfy.dry.c001|索菲亚智能暖风护理机M1|27067|
|syi.airer.d08|登帝电动晾衣架|6442|
|syi.airer.d16|卡贝电动晾衣架|5701|
|syi.airer.hkg001|豪客家电动晾衣架|5827|
|syi.airer.hsy01|宏盛远智能晾衣架|12716|
|syi.airer.sy1|卡瑞琪电动晾衣架|4194|
|syi.airer.zjl|智居乐电动晾衣架|5056|
|syniot.airer.l2|智能晾衣架|68851|
|szkj.mop.x1|顺造高温智能洗地机|6012|
|uxkeji.airer.zbs02|智帮手电动晾衣架（WIFI+BLE版）|17172|
|viomi.airer.ich108|云米互联网电动晾衣架Lite 1C|3466|
|viomi.airer.ich109|云米互联网晾衣机（母婴净菌版）|4373|
|viomi.airer.ich110|云米AI智能晾衣机Smart|8259|
|viomi.airer.ich111|云米互联网电动晾衣架Lite 1C|8263|
|viomi.airer.nch102|云米互联网晾衣机Sunny 2S|5645|
|viomi.airer.vch100|云米AI智能晾衣机Lite2（错层晾晒版）|5682|
|viomi.airer.vch103|云米互联网晾衣机Sunny 2Pro|5683|
|viomi.airer.vch104|云米AI智能晾衣机Warm 2Pro(杀菌暖烘版)|6609|
|viomi.airer.vch106|云米AI智能晾衣机Super T|11929|
|viomi.airer.vch109|云米AI智能晾衣机Super 2S|8477|
|viomi.airer.vch110|云米AI智能晾衣机Super 2Y|8478|
|viomi.airer.vch115|云米AI智能晾衣机Super 3S|23896|
|viomi.airer.vchy12|云米AI智能晾衣机 Smart S（语音版）|17357|
|viomi.airer.vchy13|云米AI智能晾衣机 Smart Pro（语音版）|17356|
|viomi.airer.vcy102|云米互联网晾衣机Sunny 2A|4886|
|viomi.airer.vcy104|云米互联网晾衣机Sunny 2A|8261|
|viomi.airer.vcy105|云米AI智能晾衣机Super|10743|
|viomi.airer.xy108|云米互联网晾衣机（阳光暖烘版）|2419|
|viomi.airer.xy108b|云米互联网晾衣机（阳光暖烘版）|7440|
|viomi.dry.v2|云米AI热泵干衣机Super 2E（10Kg 智慧柔烘）|8157|
|viomi.mop.v2|云米AI洗地机 Super 2(双刷版)|10909|
|viomi.vacuum.v11|云米互联网扫拖机器人 视觉导航版|67980|
|viomi.vacuum.v12|云米互联网扫拖机器人X2（激光导航版）|68005|
|viomi.vacuum.v13|Viomi V3|68241|
|viomi.vacuum.v15|云米AI扫拖机器人Alpha 2 Pro|69398|
|viomi.vacuum.v17|云米互联网集尘扫拖机器人|69619|
|viomi.vacuum.v20|云米集尘扫拖机器人凌厉-UV|71566|
|viomi.vacuum.v21|云米集尘扫拖机器人ALPHA-UV|71605|
|viomi.vacuum.v24|云米5GIOT扫拖机器人凌厉 2|72141|
|viomi.vacuum.v25|云米互联网扫拖机器人X3|72142|
|viomi.vacuum.v27|云米AI扫拖机器人 Alpha 2 Plus|72349|
|viomi.vacuum.v29|云米互联网扫拖机器人Eagle|72397|
|viomi.vacuum.v3|云米互联网扫地机 Pro|66085|
|viomi.vacuum.v37|云米AI集尘扫拖机器人Alpha Lite|73648|
|viomi.vacuum.v45|云米AI洗烘除菌扫拖机器人Alpha 3|74907|
|viomi.vacuum.v49|云米AI全能扫拖机器人Alpha 3 Pro|76176|
|viomi.vacuum.v6|云米扫地机器人PRO|66708|
|viomi.washer.s1|云米互联网波轮洗衣机（9KG）|66504|
|viomi.washer.sd10|云米AI洗烘一体机 Super 2 Max (12KG)|13396|
|viomi.washer.sd11|云米AI洗衣机Super 2E（10Kg DD直驱）|13916|
|viomi.washer.sd13|云米AI洗烘一体机Super 2Pro(10kg新风滚筒)|15369|
|viomi.washer.sd14|云米AI洗烘机 Super 2S(10kg全嵌智投）|17824|
|viomi.washer.sd15|云米AI洗烘机 Master 3E（10kg全嵌智投）|24302|
|viomi.washer.u1|云米洗衣机（9kg/10kg语音版）|640|
|viomi.washer.u2|云米互联网洗烘一体机|872|
|viomi.washer.u3|云米互联网洗衣机（8KG）|65800|
|viomi.washer.u4|云米互联网洗衣机（10KG）|65801|
|viomi.washer.u5|云米洗烘一体机（10kg语音版）|953|
|viomi.washer.v10|云米互联网洗烘一体机（8kg尊享版）|67179|
|viomi.washer.v11|云米互联网洗烘一体机（10kg尊享版）|67178|
|viomi.washer.v13|云米洗烘一体机Neo（10kg）|68066|
|viomi.washer.v14|云米洗衣机Neo（10kg）|68067|
|viomi.washer.v17|云米互联网洗烘一体机Eyebot|68982|
|viomi.washer.v18|云米互联网洗烘机EyeBot Face新风速烘11kg|68983|
|viomi.washer.v19|云米洗烘一体机Neo（10kg直驱版）|69181|
|viomi.washer.v20|云米洗烘一体机（10kg领航版/智航版）|69182|
|viomi.washer.v21|云米洗衣机（10kg领航版/智航版）|69183|
|viomi.washer.v22|coKiing AI洗烘一体机Royal(智能投放版)|69931|
|viomi.washer.v23|云米互联网洗衣机Master（8KG）|70400|
|viomi.washer.v24|云米互联网洗衣机Master（10KG）|70401|
|viomi.washer.v25|云米互联网洗烘一体机Master（10KG）|70402|
|viomi.washer.v26|云米互联网洗烘一体机Neo2Pro(10kg DD直驱)|70737|
|viomi.washer.v27|云米互联网洗衣机Neo2Pro(10kg DD直驱)|70738|
|viomi.washer.v28|云米互联网洗烘一体机Neo2(10kg 智能投放)|70739|
|viomi.washer.v32|云米互联网洗衣机EyeBot(12KG 智目洗版)|71194|
|viomi.washer.v33|云米互联网洗烘机Master 2 智能投放 10kg|4311|
|viomi.washer.v34|云米互联网洗烘机Master 2S 紫外除菌 10kg|4313|
|viomi.washer.v35|云米互联网洗烘机Master 2PRO 蒸汽护理10kg|4314|
|viomi.washer.v36|云米互联网洗烘机Neo2S 紫外除菌 10kg|4317|
|viomi.washer.v38|云米互联网洗烘机Master 2Mix 智目版 10kg|4569|
|viomi.washer.v4|云米互联网洗烘一体机（8KG乐享版）|66521|
|viomi.washer.v40|云米互联网洗烘机Neo3 智目版 10kg|4571|
|viomi.washer.v41|云米AI洗烘机 新风速烘版 10kg|4572|
|viomi.washer.v46|云米互联网洗烘机Neo2S 紫外除菌 10kg|9132|
|viomi.washer.v5|云米互联网洗烘一体机（10KG乐享版）|66790|
|viomi.washer.v6|云米互联网洗烘一体机Rose 9kg|66789|
|viomi.washer.v7|云米互联网洗烘一体机Neo（8kg OTA版）|67003|
|viomi.washer.v8|云米互联网洗烘一体机Neo（10kg OTA版）|67002|
|viomi.washer.w1|云米互联网壁挂洗衣机 小新|70007|
|whykid.cleaner.wk002|whykid吸尘器|22877|
|xhuan.airer.sm01|苏米隐形智能晾衣机|39011|
|xiaomi.airer.maxb|米家智能晾衣机 3 MAX|35548|
|xiaomi.airer.pro2|米家智能晾衣机 2 Pro|23721|
|xiaomi.airer.pro3|米家智能晾衣机Pro|20563|
|xiaomi.vacuum.ov21cn|米家扫拖机器人 5 Pro|21540|
|xiaomi.vacuum.ov31cn|米家扫拖机器人 M40 S|23191|
|xiaomi.vacuum.ov42cn|米家扫拖机器人 5C|24754|
|xylyj.airer.y11|米卫士晾衣架|38351|
|yankon.airer.l66|阳光智能晾衣机|8360|
|yankon.airer.v1|阳光智能晾衣架|35338|
|yeelink.airer.fold2|Yeelight 智能晾衣机 E2102|6878|
|yh1209.airer.public|勇辉智能晾衣架|5280|
|yh1209.airer.yhxm|HRLCHURE智能晾衣架|4339|
|ysm.airer.a7|熠夫人晾衣架|38580|
|yszn01.airer.krq01|卡瑞琪ProS1智能晾衣架|11160|
|yszn01.airer.krq02|卡瑞琪ProS2智能晾衣架|11161|
|yszn01.airer.lx01|晾芯M2智能电动晾衣机|26431|
|yszn01.airer.lx02|晾芯M2智能电动晾衣机Pro|26432|
|yszn01.airer.pp01|盼盼智能电动晾衣架|11868|
|yszn01.airer.pp02|盼盼智能晾衣机Y系列|26589|
|yszn01.airer.ys2102|晾芯M1智能电动晾衣机pro|7197|
|yszn01.airer.ys2103|晾芯M1智能电动晾衣机|7374|
|yunmi.airer.vch117|云米AI智能晾衣机Super 3|27819|
|yunmi.airer.vch120|云米AI智能晾衣机Super 3A|27820|
|yunmi.airer.vch122|云米蓝调智能晾衣机 S2|31269|
|yunmi.airer.vch129|云米蓝调智能晾衣机|31366|
|zhimi.vacuum.xa3|Lydsto扫拖一体机S1|73200|
|zjaupu.airer.d557|奥普晾衣机D557|10079|
|zjaupu.airer.d558|奥普晾衣机D558|10081|
|zjaupu.airer.l157s|奥普晾衣机D157S|17812|
|zjaupu.airer.l557|奥普晾衣机L557|10078|
|zjaupu.airer.l558|奥普晾衣机L558|10080|
|zjaupu.airer.lxx6|奥普烘干晾衣机|6300|
|zjaupu.airer.lxx62|奥普烘干晾衣机|7232|
|zjaupu.airer.lxx64|奥普晾衣机D157|10176|
|zjaupu.airer.lxx7|奥普摆叶烘干晾衣机|5727|
|zjdh.airer.xj003|ZJ智能晾衣架|21293|
|zjjsw.airer.sa006|JSW智能晾衣架|19053|
|zjjsw.airer.sa007|休普微-AB杆智能晾衣架|19914|

### 照明

|model|name|pd_id|
|---|---|---:|
|090615.light.ailig1|AI 色温灯(MESH)|10613|
|090615.light.cx20|平头熊F1调光磁吸灯(Mesh2.0)|24664|
|090615.light.cxlg01|PTX智能磁吸灯(MESH)|7057|
|090615.light.dd20|平头熊F1火星灯带控制器（Mesh2.0）|24665|
|090615.light.demo2|PTX智能冷暖灯带（Mesh)|3649|
|090615.light.grlg2|GR谷雨智能灯带|12346|
|090615.light.grlg3|GR谷雨智能磁吸灯|12351|
|090615.light.grlig1|GR谷雨智能天花灯|12345|
|090615.light.hycxd1|皓逸Smart Home智能磁吸灯（Mesh2.0)|26278|
|090615.light.hycxv2|皓逸专业调光磁吸灯(pro)|18665|
|090615.light.hyd300|皓逸 Smart Home智能灯带(Mesh2.0)|26381|
|090615.light.hyddv2|皓逸专业调光灯带 (pro)|19104|
|090615.light.hylg01|皓逸智能调光灯(MESH)|5649|
|090615.light.hylg03|皓逸智能磁吸灯(MESH)|5651|
|090615.light.hypro7|皓逸专业调光筒射灯(pro)|17935|
|090615.light.hyrgb1|皓逸全彩音乐律动控制器（mesh）|12945|
|090615.light.hyshsd|皓逸Smart Home智能筒射灯(Mesh2.0)|25958|
|090615.light.k1pro1|平头熊K1 Pro调光筒射灯(Mesh2.0)|29162|
|090615.light.kylg02|皓逸智能双色灯带(MESH)|5650|
|090615.light.mdd02|PTX 智能双色调光灯带(MESH)|4945|
|090615.light.milg03|PTX 深度调光灯(MESH)|13427|
|090615.light.milg05|平头熊F1调光筒射灯(Mesh2.0)|18776|
|090615.light.mlig01|PTX智能筒灯(Mesh)|3416|
|090615.light.mlig02|PTX 智能深度调光灯(MESH)|4924|
|090615.light.mtmqts|沃铁智能筒射灯(MESH 2.0)|25479|
|090615.light.mylg04|深度双色温调光驱动(V2pro)|15169|
|090615.light.pblg01|PTX 智能平板灯|8155|
|090615.light.pipadd|噼啪智能灯带(mesh)|4451|
|090615.light.pipatd|噼啪智能防眩灯(mesh)|4286|
|090615.light.rgblg|PTX全彩音乐律动控制器|8315|
|090615.light.sdcx1|PTX 深度调光磁吸灯(V2pro)|18300|
|090615.light.wtmqcx|沃铁智能磁吸灯(MESH 2.0）|25907|
|090615.light.wtmqdd|沃铁智能调光灯带（MESH 2.0）|25766|
|090615.light.xdlig|PTX 冷暖色吸顶灯(MESH)|14318|
|090615.light.xrlig1|仙人掌照明|5987|
|397.light.hallight|星辰智能吸顶灯|1080|
|704719.light.jddd|简顿智能护眼灯带|40484|
|704719.light.jdfsd|简顿风扇灯|32371|
|704719.light.lmpjmd|简顿柔光母婴灯|30260|
|704719.light.w00a01|简顿落地护眼灯5代PRO|33578|
|704719.light.wy0a01|简顿智能筒射灯|29207|
|704719.light.wy0a02|简顿智能吸顶灯|29253|
|704719.light.wy0a03|简顿吸顶灯|33307|
|704719.light.wy0a05|简顿护眼吊灯|36826|
|704719.light.wy0a06|简顿护眼灯带|37064|
|704719.light.wy0a07|简顿护眼筒射灯|37352|
|704719.light.wy0a08|简顿护眼吸顶灯|37359|
|704719.light.wyfa02|简顿高亮护眼风扇灯|37135|
|abhome.light.wy0a01|萨瑟兰情景智能灯带|25693|
|abhome.light.wy0a02|萨瑟兰情景智能筒射灯|25694|
|abhome.light.wy0a03|萨瑟兰智能磁吸灯|26714|
|aikeji.light.wy0a01|AKG智能灯带3.0|38415|
|aikeji.light.wy0a02|AKG智能筒射灯3.0（超省电）|38553|
|aikeji.light.wy0a04|AKG智能磁吸灯3.0|40870|
|aikhsp.light.wy0a01|AIKHSP情景智能灯带|40783|
|aimore.light.230915|智能冷暖吸顶灯A2|17150|
|aimore.light.240407|aimore智能冷暖吸顶灯MESH|20328|
|aimore.light.241120|aimore智能节律灯Mesh2.0|24625|
|aimore.light.cw3201|智能冷暖吸顶灯|8450|
|aiwk.light.wy0a01|AIWK情景智能磁吸射灯Live|35981|
|ajm.light.wy0a01|艾简美智能调光灯带A1|33730|
|alight.light.azcxd1|光缓智能双色温磁吸灯Pro|39493|
|alight.light.azdcdm|光缓智能淡彩光灯带Pro|37808|
|alight.light.azdd1|光缓智能双色温灯带Pro|38384|
|alight.light.aztsd1|光缓智能双色温筒射灯Pro|38383|
|alight.light.wy0a01|AZ智能情景灯|17667|
|alight.light.wy0a02|艾泽光缓筒射灯ULTRA|25695|
|alight.light.wy0a03|艾泽光缓磁吸灯ULTRA|25696|
|alight.light.wy0a04|艾泽光缓灯带ULTRA|25698|
|andi.light.wy0a02|ZXWL智能灯带3.0|37647|
|andi.light.wy0a04|ZXWL智能筒射灯3.0（超省电）|40875|
|andi.light.wy0a05|ZXWL智能磁吸灯3.0|40876|
|aozzo.light.plv2a2|奥朵高端吊灯A2|33662|
|aozzo.light.wy0a01|奥朵高端吸顶灯A1|32699|
|aozzo.light.wy0a06|奥朵高端吊灯Pro1|37071|
|aozzo.light.wy0a07|奥朵高端吸顶灯Pro1|37091|
|app.light.wynd1|诺度智能客厅灯|1832|
|arclux.light.aktsd|Arclux智能筒射灯（Mesh2.0）|39192|
|arclux.light.wy0a01|Arclux智能射灯|32407|
|arrow.light.wb5s01|箭牌照明护眼灯|26802|
|arrow1.light.wy0a01|箭ARROW智能筒射灯|31229|
|arrow1.light.wy0a02|箭ARROW智能吸顶灯A|31239|
|arrow1.light.wy0a03|箭ARROW智能吸顶灯B|31245|
|arrow1.light.wy0a04|箭ARROW智能吊灯C|31246|
|arrow1.light.wy0a05|箭ARROW智能吸顶灯C|33265|
|arrow1.light.wyfa01|箭ARROW智能风扇灯A|31250|
|arrow1.light.wyfa02|箭ARROW智能风扇灯B|31262|
|asdds.light.wyfpj1|菲普家智能灯具|1862|
|atmkn.light.wy0a01|康霓智控防眩筒射灯K1|29130|
|atmkn.light.wy0a02|康霓智控线性灯K2|29879|
|aupu.light.mesh01|AUPU奥普智能平板灯-S20M|29135|
|aupu.light.mesh60|AUPU奥普智能平板灯-S24M|31124|
|aupu.light.meshyg|AUPU奥普智能阳光平板灯-Y1M|31132|
|ax01.light.wy0a01|AX智能筒射灯|37854|
|babai.light.sl01m|Ai 智能色温灯(MESH)|12607|
|babai.light.tf31a|泰孚灯控器|69929|
|baizi.light.wy0a02|百孜智能护眼吸顶灯|35107|
|basidi.light.txddm2|Basidimo智能灯带|33756|
|bean.light.lt07|智能双色灯P7-Mesh版|17668|
|beig.light.s660v|Eiperfic 智能灯 iSulight|15786|
|beiyun.light.260c|seebest照云吸顶灯|6823|
|beiyun.light.chanyi|方响蝉翼吸顶灯|5679|
|beiyun.light.hane|韩娥音响吊灯|7731|
|bfl1.light.wy0a01|宝菲利智能筒射灯（Mesh2.0）|31093|
|binai.light.bncxdm|BNZND智能磁吸灯|35507|
|binai.light.bnddm|BNZND智能灯带|35508|
|binai.light.bntsdm|BNZND智能筒射灯|35411|
|binni.light.bnbsd|宾尼优享灯Pro|34387|
|binovo.light.rgb01|纳拓拾音星河灯GC12S|24471|
|bjl.light.wy0a01|宝嘉丽智能吊灯|37264|
|bl6969.light.wy0a01|金竞情景智能灯带SH2.0|34342|
|blx888.light.puddm|Bridgelux智能灯带(Mesh2.0)|37351|
|blx888.light.puddp|Bridgelux智能灯带Pro(Mesh2.0)|37548|
|blx888.light.wyra01|普瑞RGBW全色域灯带|27986|
|bogin8.light.wy0a01|柏晶智能射灯|31463|
|bogin8.light.wy0a02|柏晶智能灯带|32406|
|bokee.light.bkcxd|铂刻之光磁吸灯Ultra|38095|
|bokee.light.bkdd|铂刻之光灯带Ultra|38096|
|bokee.light.bkktsd|铂刻之光全色域筒射灯|38114|
|bokee.light.bktsd|铂刻之光筒射灯Ultra|38093|
|bokee.light.wy0a01|铂刻之光智能筒射灯|26805|
|bokee.light.wy0a02|铂刻之光智能磁吸灯|26829|
|bokee.light.wy0a03|铂刻之光智能灯带|26830|
|borlle.light.bl355x|Borlle全域晴空吸顶灯|30817|
|box.light.w00a01|BOXLAMP星空灯|18062|
|brm.light.wy0a01|博尔美情景智能射灯|33308|
|broway.light.bemcd|博尔美智能RGBCW幻彩灯带|39279|
|broway.light.bemdd|博尔美智能双色温灯带|39278|
|bsdy.light.bscxdm|BAOS磁吸灯|33788|
|bsdy.light.bsddm|BAOS灯带|33787|
|bsdy.light.bssdm|BAOS射灯|33786|
|bsdy.light.bstdm|BAOS筒灯|33785|
|bsdy.light.wy0a01|BS智能筒射灯|22782|
|bsdy.light.wy0a02|BS智能磁吸灯|22789|
|bsl.light.3101yh|贝视朗学习灯|34531|
|bsr.light.bsrtsd|百士瑞智能筒射灯（Mesh2.0）|35062|
|bt166.light.wy0a01|博途智能筒射灯|34101|
|bt166.light.wy0a03|博途智能磁吸灯|37524|
|bt166.light.wy0a04|博途智能灯带|37706|
|bt166.light.wy0a05|博途智能吸顶灯|38207|
|btg.light.btgm24|泰姬光零频闪灯带控制器|23470|
|btg.light.btgz24|泰姬光零频闪灯带控制器|27846|
|btzn.light.v1|比特灯光|71301|
|bull.light.fan02|公牛风扇灯F18B|34206|
|bull.light.fan03|公牛风扇灯F22C|35314|
|bull.light.fan04|公牛风扇灯F06E|35315|
|bull.light.fan05|公牛风扇灯F00CM|36089|
|bull.light.fan06|公牛风扇灯F18C|38240|
|bull.light.fan07|公牛风扇灯F22D|38241|
|bull.light.jld01|公牛吸顶灯M22-100W|31835|
|bull.light.mlg03|公牛L03智能调光灯带|33766|
|bull.light.mz02|公牛智能双色温灯带|34747|
|bull.light.ts01|公牛筒灯T06-9W|39292|
|bull.light.wy0a01|公牛灵犀MT02智能射灯|33614|
|bull.light.x19a|公牛吸顶灯X19-150W|31443|
|bull.light.x19b|公牛吸顶灯X19-55W|31824|
|bull.light.x19c|公牛吸顶灯X19-48W|31825|
|bull.light.x19d|公牛吸顶灯X19-36W|31826|
|bull.light.xc03a|公牛吸顶灯XC03-230W|34256|
|bull.light.xc03b|公牛吊灯XC03-180W|34259|
|bull.light.xc03c|公牛吊灯XC03-80W|34258|
|bull.light.xc03d|公牛吸顶灯XC03-55W|34257|
|bull.light.xc04a|公牛吸顶灯XC04-195W|34260|
|bull.light.xc04b|公牛吊灯XC04-58W|34262|
|bull.light.xc04c|公牛吸顶灯XC04-55W|34261|
|bull.light.xd05a|公牛吸顶灯XD05-150W|34525|
|bull.light.xd05b|公牛吸顶灯XD05-55W|34592|
|bull.light.xd05c|公牛吸顶灯XD05-48W|34593|
|bull.light.xd05d|公牛吸顶灯XD05-36W|34594|
|bull.light.xd08a|公牛吸顶灯XD08-150W|36520|
|bull.light.xd08b|公牛吸顶灯XD08-50W|36521|
|bull.light.xd09a|公牛吸顶灯XD09-150W|36522|
|bull.light.xd09b|公牛吸顶灯XD09-50W|36524|
|bull.light.xj01a|公牛吸顶灯XJ01-150W|40040|
|bull.light.xj01b|公牛吸顶灯XJ01-55W|40039|
|bull.light.xj01c|公牛吸顶灯XJ01-48W|40038|
|bull.light.xj03a|公牛吸顶灯XJ03-225W|40034|
|bull.light.xj03b|公牛吸顶灯XJ03-80W|40033|
|bull.light.xj03c|公牛吸顶灯XJ03-55W|40032|
|bull.light.xj04a|公牛吸顶灯XJ04-220W|40037|
|bull.light.xj04b|公牛吸顶灯XJ04-55W|40036|
|bull.light.xj04c|公牛吸顶灯XJ04-48W|40035|
|buluce.light.0006|步路思橱柜双色温灯|31857|
|bxy.light.bxyts1|梓阳全屋智能筒射灯Mesh2.0|38508|
|bymiot.light.ctlv1|未来居调光灯（冷暖）|78851|
|bymiot.light.ctwlv1|未来居无线筒射灯调光驱动器|73613|
|bymiot.light.dcwlv1|未来居无线单路控制器|73634|
|bymiot.light.dmv1|未来居调光灯（彩光）|78853|
|bymiot.light.dmwlv1|未来居无线灯带调光驱动器|73636|
|bymiot.light.dmwlv2|未来居无线彩光灯带驱动器|75455|
|bymiot.light.lumv1|未来居调光灯（亮度）|78846|
|bymiot.light.plcv1|未来居PLC恒流驱动电源|81737|
|bymiot.light.plcv2|未来居PLC恒压驱动电源|81738|
|bymiot.light.rgbv1|未来居调光灯（彩色）|78852|
|bymiot.light.wljtsd|未来居智能筒射灯(巨省电)|36631|
|bymiot.light.wlv10|未来居Mesh智能磁吸泛光灯Ultra|26352|
|bymiot.light.wlv11|知或居Mesh智能磁吸灯（2.0版）|26423|
|bymiot.light.wlv12|知或居Mesh智能线性灯（2.0版）|26424|
|bymiot.light.wlv13|知或居Mesh智能筒射灯（2.0版）|26425|
|bymiot.light.wlv14|未来居Mesh智能灯带Ultra|26426|
|bymiot.light.wlv2|未来居智能调光灯(MESH)|21168|
|bymiot.light.wlv3|未来居轻连调光灯带控制器（Mesh 2.0）|21831|
|bymiot.light.wlv4|未来居无线镜子灯带控制器|81090|
|bymiot.light.wlv5|未来居智能射灯（mesh 2.0）|23073|
|bymiot.light.wlv8|未来居Mesh智能磁吸格栅灯Ultra|25121|
|bymiot.light.wlv9|未来居Mesh智能磁吸射灯Ultra|26351|
|careco.light.track|车顶滑轨灯|23403|
|careco.nlight.o654|小米汽车磁吸补光灯|25190|
|cbu.light.wy0a02|超步线形氛围灯|38394|
|ccdq.light.c01|长城智能吸顶灯PRO|30942|
|cchip.light.l1|天际快装吸顶灯|2915|
|cd168.light.cd001|YETFIF智能筒射灯（Mesh2.0）|25986|
|cd168.light.cd5lcd|YETFIF五路智能灯带(Mesh2.0)|32991|
|cd168.light.cdcxdm|YETFIF智能磁吸灯（Mesh2.0）|28593|
|cd168.light.cddd01|YETFIF智能灯带Ultra|40080|
|cd168.light.cdts01|YETFIF智能筒射灯Ultra|38310|
|cd168.light.v8hsm|YETFIF智能灯带（Mesh2.0）|28003|
|cd168.light.wy0a01|YETFIF智能筒射灯|26138|
|cd168.light.wy0a02|YETFIF智能灯带|30646|
|cdblm.light.dkjdlm|灯科及第智能筒射灯（Mesh2.0）|29703|
|cddz.light.cdygd1|Jiuhao橱衣柜灯带（Mesh2.0）|38134|
|cdlzm.light.llyddm|鲁莱雅智能灯带（Mesh2.0）|29255|
|cdlzm.light.llyznd|鲁莱雅智能筒射灯（Mesh2.0）|23849|
|cdn.light.1075|西顿舍见智能调光P70筒射一体款|20237|
|cdn.light.12w1o|西顿舍见恒流PLC调光驱动器|77564|
|cdn.light.12w2o|西顿舍见恒流PLC调色温驱动器|77565|
|cdn.light.150w1o|西顿舍见恒压PLC调光驱动器|77569|
|cdn.light.150w2o|西顿舍见恒压PLC调色温驱动器|77570|
|cdn.light.150w5o|西顿舍见PLC恒压RGBCW驱动器|77571|
|cdn.light.75w1o|西顿舍见恒压PLC调光驱动器 75W|77566|
|cdn.light.75w2o|西顿舍见恒压PLC调色温驱动器 75W|77567|
|cdn.light.75w5o|西顿舍见PLC恒压RGBCW驱动器 75W|77568|
|cdn.light.cx01|西顿舍见PLC磁吸灯(调光)|79948|
|cdn.light.cx02|西顿舍见PLC磁吸灯(调色)|79949|
|cdn.light.fsd|西顿智能风扇灯|30329|
|cdn.light.galaxy|西顿舍见晴空吸顶灯|21538|
|cdn.light.k200|西顿舍见PLC开关控制器|79135|
|cdn.light.pcstsd|西顿PLC恒流驱动器（调色）|82320|
|cdn.light.plccxd|西顿PLC磁吸灯（调色）|82319|
|cdn.light.plcdd|西顿PLC恒压驱动器（调色）|82321|
|cdn.light.rtczgy|西顿 Yu人体存在感应灯|26454|
|cdn.light.sjbx2|西顿RGBCW幻彩灯带|36866|
|cdn.light.td001|西顿舍见PLC转0-10V控制器(调光)|79578|
|cdn.light.td002|西顿舍见PLC转0-10V控制器(调色)|79581|
|cdn.light.w00a02|西顿单色灯带|7945|
|cdn.light.w00a03|西顿舍见LED杀菌厨卫灯|15937|
|cdn.light.w00a05|西顿单色温智能筒射灯M2|23446|
|cdn.light.w00a06|西顿单色温智能灯带M2|23447|
|cdn.light.wy0a01|西顿26系列智能射灯|4306|
|cdn.light.wy0a03|西顿36系列智能射灯|5011|
|cdn.light.wy0a04|西顿恒流智能驱动|5012|
|cdn.light.wy0a05|西顿双色灯带|7944|
|cdn.light.wy0a06|西顿照明智能灯D|18228|
|cdn.light.wy0a07|西顿照明智能灯HL|18229|
|cdn.light.wy0a08|西顿照明智能灯X|18230|
|cdn.light.wy0a09|西顿照明智能灯XL|20297|
|cdn.light.wy0a10|西顿照明智能灯DL|20298|
|cdn.light.wy0a11|西顿双色温智能筒射灯M2|23352|
|cdn.light.wy0a12|西顿双色温智能灯带M2|23357|
|cdn.light.wy0a14|西顿 Yu智能灯带电源|25952|
|cdn.light.wyra01|西顿舍见星河幻彩吊灯|29683|
|cdn.light.wyrh2|西顿智能吸顶灯H2|27608|
|cdn.light.xdcxm2|西顿智能磁吸灯M2|27700|
|cdn.light.xdcxm3|西顿智能磁吸灯（单色温）M2|32035|
|cdn.light.xdicl|西顿照明吸顶灯|29076|
|cdn.light.xdtjd2|西顿天空灯青春版|39252|
|cdn.light.xhxdd|西顿天空灯|31281|
|cdn.light.xidbv2|西顿金山系列吊灯|39452|
|chim.light.wy0a01|龙辕情景智能筒射灯|30830|
|chint.light.chint1|正泰智能吸顶灯|6328|
|chuangmi.light.028a01|小白智能看护灯|69985|
|chuangmi.light.716a02|小白智能筒射灯|8371|
|chuangmi.light.717a02|小白智能灯带|8372|
|chuangmi.light.718a02|小白智能磁吸灯|8373|
|chuangmi.light.727a02|小白智能筒射灯（专业版）|13124|
|chuangmi.light.738a02|小白智能灯带（专业版）|13817|
|chuangmi.light.739a02|小白智能磁吸灯（专业版）|14113|
|ciheng.light.wy0a01|磁恒智能灯带控制器|27383|
|ciheng.light.wy0a02|CIIHEN智能灯带|32408|
|clk.light.basket|兀坐提篮|3292|
|clouds.light.wy0a01|云睐智能筒射灯（Mesh2.0）|31173|
|clouds.light.wy0a02|云睐智能磁吸灯（Mesh2.0）|31176|
|clouds.light.wy0a03|云睐智能灯带（Mesh2.0）|31177|
|cnl.light.xltfl|雪莱特护眼落地灯|23469|
|comely.light.wy0a01|新特丽智能照明|15124|
|comely.light.wy0a02|新特丽智能灯具|15214|
|comely.light.wy0a03|新特丽天际线智能餐吊灯|18663|
|cqzx.light.wy0a01|智信物联深度防眩射灯ZX-SL09|24292|
|creat6.light.lt07|ANKOTTI安科帝智能灯|21568|
|crzm.light.w00a01|NW耐为简致点护眼无频闪单色智能灯带|2292|
|crzm.light.wy0a01|NW耐为简致点护眼无频闪三色智能灯带|2293|
|crzm.light.wy0a02|耐为简致点防眩光高显射灯pro1|3619|
|crzm.light.wy0a03|耐为简致点高显磁吸氛围灯pro1|3778|
|crzm.light.wy0a04|耐为简致点护眼无频闪三色智能灯带|5473|
|csx.light.wy0a01|留虹智能筒射灯|24909|
|csykj.light.xyznj|芯毅智能浴室镜灯|26680|
|cszndy.light.cszndd|COSUO智能灯带(Mesh2.0)|33686|
|cuco.light.sl4|电小酷彩色智能灯带SL4|70811|
|cuco.light.sl4a|电小酷智能灯带SL4|72875|
|cuco.light.wb2m|电小酷智能白灯WB2-M|72516|
|cuco.light.wb2mn|电小酷智能白灯WB2-M|74751|
|cuco.light.wb5m|电小酷智能彩灯WB5-M|72517|
|cuco.light.wb5mn|电小酷智能彩灯WB5-M|74750|
|cxds.light.wymz01|木子智能灯|1866|
|cxled.light.wy0a01|XIERD智能吸顶灯|38729|
|cxw.light.wyfv01|Mesh风扇灯系列V1|15365|
|cxw.light.wyv02|Mesh色温灯系列V2|17098|
|cxznkj.light.wy0a01|智邦熊智能筒射灯UItra2.0|35370|
|cxznkj.light.wy0a02|智邦熊智能灯带UItra2.0|35371|
|cxznkj.light.wy0a03|智邦熊智能磁吸灯UItra2.0|35372|
|czhkj.light.l0523|乐天派灯带魔方版|38234|
|daolai.light.dlb001|LED情景灯Mesh版|3558|
|daolai.light.dls002|智能Mesh色温灯Pro|10450|
|daolai.light.dls006|智能WiFi色温灯Pro|12115|
|daolai.light.qp320|熠世华彩双色LED灯泡V1|5416|
|daolai.light.qp350|熠世华彩流光LED灯泡V1|5317|
|daolai.light.sd330|熠世华彩射灯|4600|
|daolai.light.xd340|熠世华彩吸顶灯|4610|
|daowei.light.wy0a02|道韦DL系列智能筒射灯|37181|
|ddjzm.light.wy0a01|帅灯堡智能吸顶灯|3215|
|ddk.light.wy0a01|NIOYE智能灯|2131|
|ddk.light.wyra01|NIOYE全彩LED灯|3330|
|ddk.light.wyra02|NIOYE音乐律动全彩灯|4423|
|ddk.light.wyra03|NIOYE智能彩光灯|5266|
|ddy.light.clhad|小蓝灯|27347|
|devcea.light.ls2302|宜家麦希瑟E27 600lm智能球泡灯|14905|
|devcea.light.ls2303|宜家麦希瑟E27 1055lm智能球泡灯|14908|
|devcea.light.ls2304|宜家麦希瑟E14 470lm智能球泡灯|14909|
|devcea.light.ls2305|宜家麦希瑟E14 470lm智能烛泡灯|14910|
|devcea.light.ls2306|宜家麦希瑟GU10 345lm智能射灯|14911|
|devcea.light.ls2307|宜家麦希瑟E27 806lm智能彩色球泡灯|14912|
|dhzm.light.wy0a01|灯寰简约卧室灯|5491|
|didi.light.v8ssm|digad智能台灯A1|29645|
|dijia.light.wy0a01|万里扬智能筒射灯|38314|
|dikair.light.wy0a01|丹菲诺智能灯|4565|
|dikair.light.wy0a02|宣艺智能灯|4566|
|dikair.light.wy0a03|研泰情景智能灯|4567|
|dikair.light.wy0a04|易唐智能灯|4568|
|dj1587.light.wy0a01|灯简智能灯|12560|
|djzm01.light.wy0a02|DINGJIAN智能筒射灯|40505|
|dlmz.light.wy0a03|灯乐美防眩护眼筒射灯|38033|
|dlx.light.cw790|德力西电气智能厨卫灯|32867|
|dlx.light.dlxxdd|德力西电气智能吸顶灯|34776|
|dlx.light.eps118|德韵智能简约家居灯|7681|
|dlx.light.eps119|德韵智能现代家居灯|7680|
|dlx.light.lamp01|德力西智能护眼吸顶灯|29009|
|dlx.light.lgt001|德力西电气智能射灯|30433|
|dlx.light.lgt002|德力西电气智能筒灯|30656|
|dlx.light.lgt003|德力西电气智能灯带|30657|
|dlzm.light.wyfa01|风行四野智能风扇灯|30988|
|dmb827.light.wy0a01|DMB智能筒射灯|33649|
|dmb827.light.wy0a02|DMB智能灯带|33650|
|dmq.light.wy0a01|迪木茜智能筒灯|3664|
|dnake.light.lgt002|狄耐克双色温射灯(Mesh2.0)|31723|
|dnake.light.lgt003|狄耐克双色温灯带(Mesh2.0)|31724|
|dnake.light.lt07|狄耐克LED控制装置（蓝牙Mesh调光调色）|21469|
|doke.light.wy0b01|东刻智能筒射灯|39223|
|dong.light.wy0a01|东东简约智能客厅灯|4688|
|doonne.light.002|智步楼梯灯ZM1|20878|
|doonne.light.h1|μ-home物联网楼梯灯|27942|
|doonne.light.pir01|智步人体感应氛围灯|27075|
|doonne.light.rgbcw5|智步极光灯ZC5|32764|
|dosin1.light.dsem20|DOSIN智能灯带|38502|
|dotdot.light.dian24|点点Diandian皓光24w|2331|
|dotdot.light.dian45|点点Diandian皓光45w|2332|
|dotdot.light.dian90|点点Diandian皓光90w|2333|
|dreame.light.r2229|米家皮皮灯|9162|
|dreame.light.zmf02b|追觅智能筒射灯|31739|
|dreame.light.zmf03b|追觅智能双色灯带 S20|37176|
|drui.light.wy0a01|亿来嘉DRUI智能灯带(MESH 2.0)|33817|
|drui.light.wy0a02|亿来嘉DRUI智能磁吸灯(MESH 2.0)|33818|
|drui.light.wy0a03|沃铁WT智能灯带(MESH 2.0)|34731|
|drui.light.wy0a04|沃铁WT智能磁吸灯(MESH 2.0)|34732|
|drui.light.yljdd|沃铁超低功耗智能灯带（Mesh2.0）|40733|
|dwy123.light.wy0a01|灯无忧智能吸顶灯|36673|
|dxzm.light.dxcx1|GAMON智能磁吸灯|38927|
|dyds01.light.dayblb|广顿照明智能球泡灯|34208|
|efe888.light.wy0a01|意菲意LED智能吸顶灯|32755|
|efe888.light.wy0a02|意菲意智能吸顶灯|32756|
|euty.light.wy0a01|欧铁智能筒射灯|26667|
|euty.light.wy0a02|欧铁智能灯带|26681|
|euty.light.wy0a03|欧铁智能磁吸灯|26682|
|ezhome.light.l0001|智汇云全彩音乐律动控制器|11600|
|fangdi.light.fgc001|MixDALI调光调色灯|17187|
|fantq0.light.wy0a02|方塔希Essence双色温光伴侣|21744|
|feid.light.fddd|飞雕智淳智能灯带|39817|
|feid.light.fdtsd|飞雕智淳智能筒射灯|39800|
|fkyc88.light.wy0a01|非克云仓智能双色温射灯|31399|
|flkj.light.wy0a01|菁雅情景智能嵌入筒射灯G1|32111|
|fooc.light.wy0a05|FOOC星空智能嵌入式射灯|37309|
|fooc.light.wy0a06|FOOC星空智能嵌入式筒灯|37344|
|fookes.light.fkscxd|FOOKES智能磁吸灯（Mesh2.0）|34232|
|fookes.light.fksddm|FOOKES 智能灯带|29911|
|fookes.light.fksts1|FOOKES智能筒射灯（Mesh2.0)|38429|
|fookes.light.fksznd|FOOKES智能灯带（Mesh2.0）|34234|
|ftd.light.cwrgb1|FTD智能彩光灯(MESH)|21707|
|ftd.light.dsplmp|智能双色灯V3(MESH)|13233|
|ftd.light.dupont|杜邦智能照明|17333|
|ftd.light.flpryz|日月盒子无叶风扇灯|23512|
|ftd.light.ftdlmp|智能双色灯V2(MESH)|12066|
|ftd.light.hglmp|悍高智能柜类灯(MESH)|17007|
|ftd.light.lmpami|AMI智能灯|18207|
|ftd.light.lmpfan|智能风扇灯V1(WIFI)|19144|
|ftd.light.lmpswi|FTD智能双色灯S(WIFI)|22125|
|ftd.light.lmpyil|YL智能无主灯|24858|
|ftd.light.lmpyul|RF智慧照明V1(MESH)|21164|
|ftd.light.lmpzdw|DW智能节律双色灯带|26151|
|ftd.light.lpv2sl|FTD智能双色灯V2SL(MESH)|20550|
|ftd.light.lpv3sl|智能双色灯V3SL(MESH)|19940|
|ftd.light.nomain|智能节律无主灯|19534|
|ftd.light.wfibrm|智能节律双色灯V1|17567|
|ftd.light.wfibv2|智能节律双色灯V2|20078|
|ftd.light.wfilmp|智能双色灯(WIFI)|15480|
|ftd.light.wfilv2|智能双色灯V2(WIFI)|20070|
|ftds.light.wyft1|凡童智能灯|1829|
|ftzm.light.wy0a01|智能筒射灯 蓝牙Mesh版|21330|
|ftzm.light.wy0a02|智能灯带 蓝牙Mesh版|21331|
|ftzm.light.wy0a04|FAKT智能筒射灯（Mesh2.0）|34913|
|ftzm.light.wy0a05|FAKT情景智能灯带（Mesh2.0）|34914|
|ftzm.light.wy0a06|FAKT情景智能橱柜灯带（Mesh2.0）|34915|
|gaosd.light.cctled|高事达PLC调光控制装置|79467|
|gaosd.light.cxled|高事达PLC磁吸轨道灯|79992|
|gaosd.light.gsdlcw|高事达PLC恒压灯带调光控制装置|81142|
|gayoo.light.g01cxd|光言光语 智能护眼磁吸灯Mesh2.0|30609|
|gayoo.light.gydsdd|光言光语 光域大师智能护眼线光灯带2.0|29449|
|gayoo.light.gyhsm|光言光语 智能护眼筒射灯Mesh2.0|26117|
|gayoo.light.gyhsm2|光言光语  护眼线光灯带Mesh2.0|26148|
|gczm.light.wy0a01|广磁智能筒射灯|35261|
|gdds.light.gzzfdd|高灯大师双回路智能灯带|39677|
|gdds.light.wy0a01|高灯大师智能灯|9439|
|gdds.light.wy0a02|高灯大师节律智能筒射灯|23854|
|gdled.light.wy0a01|智能小灯深防眩灯PRO|31011|
|gdlx.light.lxis01|LXIS智能筒射灯（Mesh1.0）|26993|
|gdlx.light.lxis03|LXIS智能筒射灯（Mesh2.0）|27023|
|gdmzdz.light.mzddm|名舟智能灯带（Mesh2.0）|28632|
|ge.light.mono1|X-Bulb智能灯泡|58|
|gepai.light.wy0a01|格派智能筒射灯|33081|
|gg1.light.wy0a01|简杰智能筒射灯（mesh2.0版）|25822|
|gg1.light.wy0a02|简杰 Air 3 低压灯带mesh2.0|25847|
|gg1.light.wy0a03|简杰 Air 1 磁吸灯 mesh2.0|25848|
|ghzm.light.ghcxd|冠华智能磁吸灯|39171|
|ghzm.light.ghdd|冠华智能灯带|39172|
|ghzm.light.ghtsd|冠华智能筒射灯|39170|
|giot.light.aise01|Ai智能情景WIFI双色灯|8822|
|giot.light.dblgt1|杜邦吸顶灯|16710|
|giot.light.h60301|希尔顿智能LED吸顶灯|11112|
|giot.light.h86161|希尔顿智能LED吊灯|11114|
|giot.light.hhyd1|月影智能护眼灯|15876|
|giot.light.hwzd1|月影自然光护眼无主灯|15886|
|giot.light.v10ilw|V10Gra智能学习灯（WiFi）|22454|
|giot.light.v3|V3智能色温灯（Mesh）|10437|
|giot.light.v5ssm|V5智能色温灯（Mesh）|11724|
|giot.light.v5ssw|V5智能色温灯（WiFi）|12374|
|giot.light.v8icm|V8智能彩色灯（Mesh）|17681|
|giot.light.v8ssm|V8智能色温灯（Mesh）|15504|
|giot.light.v8ssw|V8智能色温灯（WiFi）|15913|
|giot.light.v8uswd|V8Gra智能灯（Mesh2.0）|23283|
|giot.light.v9ssw|V9Gra智能色温灯（WiFi）|20765|
|giot.light.wy0a01|诺米蓝牙mesh智能灯带|18749|
|giot.light.xhyd1|希尔顿智能护眼灯|15883|
|giot.light.xwzd1|月影自然光磁吸灯|15885|
|giot.light.y60301|月影智能LED吸顶灯|11111|
|giot.light.y86161|月影智能LED吊灯|11113|
|giwu.light.wy0a01|即屋智能双色射灯G3|31398|
|gjzn.light.gjtsd1|光炯智能-筒射灯（Mesh2.0）|38489|
|glvst.light.wwgbv2|普惠护眼吸顶灯|35324|
|glvst.light.wwgv22|普惠客厅护眼吸顶灯|35325|
|gmm.light.wy0a01|双色情景智慧灯|7224|
|gmm.light.wy0a02|LED智能灯mesh|8960|
|gmm.light.wy0a05|GJ智能双色灯带|37356|
|gmn.light.wy0a01|哥曼尼G1系列吸顶灯（蓝牙Mesh版）|2741|
|gmn.light.wy0a02|哥曼尼情景双色筒灯（蓝牙mesh版）|2742|
|gmn.light.wy0a04|哥曼尼情景色温灯（MESH版）|4147|
|gmn.light.wy0w01|哥曼尼情景双色吸顶灯|1988|
|gmn.light.wyfan1|哥曼尼G1系列卧室风扇灯|2838|
|gmn.light.wyra01|GMN情景灯带（MESH版）|3840|
|goodtk.light.wy0a01|GOODTEK双色温灯带MESH2.0|38258|
|googo.light.wy0a01|mitch深度防眩智能筒射灯|26970|
|googo.light.wy0a02|mitch双色温智能灯带|26971|
|googo.light.wy0a03|mitch双色温智能磁吸灯|26972|
|gsd.light.wy0a01|QT情景Mesh智能灯|5018|
|gsd.light.wy0a08|GOLDSUNDA智能筒射灯|35533|
|gsd.light.wy0a09|GOLDSUNDA智能灯带|35534|
|gsm.light.gshxdd|广颂S1火星灯带（Mesh2.0）|38346|
|gsm.light.gszns2|广颂S1智能灯带(Mesh2.0)|27253|
|gswl.light.v9hsm1|HD智能节律灯X9|27194|
|gszm.light.pqcxdm|LEDGSX智能磁吸灯|36122|
|gszm.light.zntsdm|LEDGSX智能筒射灯|33811|
|gt1688.light.1988|自然爱星空灯 GT9|23703|
|gt1688.light.wy0a01|自然爱筒射灯DS1 2.0|25690|
|gt1688.light.wy0a02|自然爱磁吸灯MT3 Mesh2.0|25954|
|gt1688.light.wy0a03|自然爱灯带PS7 Mesh2.0|25955|
|gt1688.light.wy0a04|自然爱吸顶灯CL1 Mesh2.0|25956|
|gt1688.light.wy0a05|自然爱圈圈吊灯T1 Mesh2.0|35262|
|gtop.light.c02|智悦智能灯|9301|
|gtop.light.c04|智悦智能吸顶灯通用款|9644|
|gtop.light.c05|智悦智能吸顶灯pro|13806|
|gtop.light.c06|智悦智能led吸顶灯|13879|
|gtop.light.eps119|智悦智能吸顶灯|3987|
|gtop.light.eps120|智悦智能三线辅灯|7573|
|gtop.light.fan03|情景智能风扇灯|16213|
|gtop.light.fan04|智悦无叶清风灯|21854|
|gtop.light.gtop02|智悦智能筒射灯|6137|
|gtop.light.koey1|KOEY空气循环风扇灯|17961|
|gtop.light.xl01|智悦吸顶灯|4270|
|gtop.light.yl01|Side智能吸顶灯|14748|
|gtop.light.yl03|Yeelight智能LED吸顶灯|16426|
|guanx.light.wy0a01|GXMesh2.0智能筒射灯|24740|
|gudi.light.wy0a01|固帝智能筒射灯|34669|
|guixin.light.w00a01|U-FAMILY Mesh智能调光灯带U9|28912|
|guznos.light.gzcxdm|GZ 智能磁吸灯|29874|
|guznos.light.gzddm|GZ 智能灯带|29875|
|guznos.light.gztsdm|GZ 智能筒射灯|29872|
|gxhl.light.7zps11|7z AI灯控器|12178|
|gydz.light.blecw1|GY智能灯蓝牙Ultra版|23162|
|gydz01.light.wy0a01|家斯特智能筒射灯|36624|
|gysj.light.gysj01|光源世家护瞳系列母婴灯|35239|
|gysj.light.gysj02|光源世家光境系列舒眠灯|35241|
|gysj.light.wy0a01|光源世家小家智控洗墙灯|30255|
|gyzm.light.gycxdm|GIGIDIDI智能磁吸灯|35781|
|gzjp.light.w00a01|JP单色灯带|27127|
|gzjp.light.wy0a01|JP双色灯带|26826|
|gzkj.light.wy0a01|GZ智能灯带mesh2.0|31179|
|gzkj.light.wy0a02|GZ智能磁吸灯mesh2.0|31180|
|gzkj.light.wy0a04|GZ智能筒射灯3.0（超省电）|40858|
|gzkj.light.wyra01|GZ智能彩光灯带mesh2.0|31161|
|haier.light.wy0a03|海尔智能风扇灯|21965|
|haier.light.wy0a04|海尔智能吸顶灯（标准款）|22714|
|haoyi.light.hoy2dd|皓逸全色域灯带氛围大师Color|38164|
|haoyi.light.hoy560|皓逸全色域天境灯情景大师Color圆形|31915|
|haoyi.light.hoy6x9|皓逸全色域天境灯情景大师Color方形|31916|
|haoyi.light.hoym20|皓逸全色域筒射灯氛围大师Color|36563|
|haoyi.light.hoyrmo|皓逸全色域软膜灯氛围大师Color|38567|
|haoyi.light.hycclm|皓逸全色域磁吸灯情景大师Color|32668|
|haoyi.light.hyclm|皓逸全色域灯带情景大师 Color|32154|
|haoyi.light.hyctlm|皓逸全色域筒射灯情景大师Color|32666|
|haoyi.light.hycxdm|皓逸全色域磁吸灯情景大师Lite|29594|
|haoyi.light.hyddm|皓逸全色域灯带情景大师Lite|29781|
|haoyi.light.hypro1|皓逸射灯（Max)|20046|
|haoyi.light.hypro2|皓逸磁吸灯（Max)|20665|
|haoyi.light.hytsdm|皓逸全色域筒射灯情景大师Lite|29780|
|haoyi.light.wy0a01|皓逸24V恒压双色调光控制器|18525|
|haoyi.light.wy0a03|皓逸全光谱吸顶灯（Max）|20896|
|haoyi.light.wy0a04|皓逸智能筒射灯（Mesh2.0）|22346|
|haoyi.light.wy0a05|皓逸智能调光灯带（Mesh2.0）|24238|
|haoyi.light.wy0a06|皓逸智能磁吸灯（Mesh2.0）|24239|
|haoyi.light.wyrb01|皓逸智能望舒系列护眼吸顶灯|39310|
|hbada1.light.203|黑白调儿童智能学习桌护眼灯 S2|26334|
|hbc.light.wy0a01|皇的智能灯|2844|
|hcs.light.yssl01|智能情景调光灯|13037|
|hcznjj.light.wyll01|郞励LED吸顶灯|1863|
|hdm.light.wy08a|哈达曼智能LED吸顶灯|1824|
|hefeng.light.hftsdm|赫锋智能筒射灯（Mesh2.0）|36594|
|hekai1.light.wy0a01|桂家超薄智能灯带|33737|
|heko.light.wy0a01|KEEY-BUS调光调色控制设备|9974|
|hemu.light.hmxydm|禾木夜灯 蓝牙Mesh版|35782|
|hfua.light.hwfm20|UAFENG 智能灯带2.0|34310|
|hgkj.light.v9hsm|鸿光智能筒射灯（Mesh2.0）|32313|
|hgled.light.hgkm20|悍高智能柜类灯(MESH 2.0)|37265|
|hgzm.light.v8hsm|河光智能灯带（Mesh2.0）|28165|
|hlm.light.wy0a01|好光万变光效调角洗墙射灯猎户|32871|
|hlzm.light.heng6m|Heng6智能双色灯（Mesh2.0）|26989|
|hming.light.wy0x01|Honeywell客厅吸顶灯|32692|
|hming.light.wy0x02|Honeywell卧室吸顶灯|32693|
|hming.light.wy0x10|Honeywell卧室吸顶灯2|34104|
|hming.light.wy0x11|Honeywell客厅吸顶灯2|34233|
|hnlife.light.socd01|心新落地幻彩灯|29811|
|hnlife.light.socw01|心新落地冷暖灯|33128|
|hnn.light.ok33|HAPPY NOCNOC圆形吸顶灯|25106|
|hollki.light.wy0a01|HOLLKI-K1026智能灯带|34198|
|honkon.light.hgcxd|宏光智能磁吸灯(Mesh2.0)|33599|
|honkon.light.hgddm|宏光智能软灯带(Mesh2.0)|39448|
|honkon.light.hgtsdm|宏光智能筒射灯(Mesh2.0)|33700|
|honyar.light.hy01|鸿雁智能感应风扇灯|25639|
|honyar.light.hy02|鸿雁智能家居灯V1|26083|
|honyar.light.hycxdm|鸿雁智能磁吸灯V2|29495|
|honyar.light.hytsdm|鸿雁智能筒射灯V2|29336|
|honyar.light.hyxddm|鸿雁智能吸顶灯（Mesh2.0）|36082|
|honyar.light.radar|鸿雁智能感应面板灯|29483|
|honyar.light.td8ld1|鸿雁智能感应筒灯|29589|
|honyar.light.td8zh1|鸿雁智能筒灯|29587|
|honyar.light.th8ld2|鸿雁智能感应射灯|29590|
|honyar.light.th8zh2|鸿雁智能射灯|29588|
|honyar.light.tjdhoy|鸿雁梵高系列 智能节律幻彩灯|31593|
|honyar.light.tsdn1|鸿雁智能筒射灯DM1|35137|
|honyar.light.v8hsm|鸿雁智能灯带plus|31900|
|honyar.light.wy0a01|鸿雁智能筒射灯V1|25699|
|honyar.light.wy0a02|鸿雁智能灯带V1|25700|
|honyar.light.wy0a03|鸿雁智能磁吸灯V1|27454|
|honyar.light.wy0a05|鸿雁智能筒射灯|34017|
|hszn.light.v8hsm|华时智能筒射灯（Mesh2.0）|28009|
|hszn.light.v8hsm1|华时智能灯带（Mesh2.0）|28008|
|hszn.light.wy0a01|华时智能吸顶灯（Mesh2.0）|34625|
|hszna.light.hl001|辉帅智能调光灯带|34724|
|hszna.light.hl002|辉帅智能调光筒射灯|34725|
|huafu.light.hftsdm|HF智能筒射灯（Mesh2.0）|34066|
|huayi.light.aqu114|慧作水瓶星彩泡|1901|
|huayi.light.ari013|慧作白羊星卧室系列吸顶灯|1707|
|huayi.light.aries|慧作白羊星客厅系列吸顶灯|1464|
|huayi.light.fanwy|慧作新风照明风扇吸顶灯|1314|
|huayi.light.fanwy2|慧作新风照明(2020版)|3230|
|huayi.light.kin1|慧作巨蟹星灯带|1812|
|huayi.light.kin2|慧作巨蟹星灯带Pro|1813|
|huayi.light.peg091|慧作天马星客厅系列吸顶灯|1757|
|huayi.light.peg093|慧作天马星卧室系列吸顶灯|1758|
|huayi.light.pis123|慧作双鱼星卧室系列吸顶灯|1668|
|huayi.light.pisces|慧作双鱼星客厅系列吊灯|1465|
|huayi.light.rgb205|慧作慧光板|3795|
|huayi.light.tau023|慧作金牛星卧室系列吸顶灯|1699|
|huayi.light.taurus|慧作金牛星客厅系列吸顶灯|1698|
|huayi.light.vir063|慧作处女星卧室系列吸顶灯|1670|
|huayi.light.virgo|慧作处女星客厅系列吸顶灯|1467|
|huayi.light.wy|慧作吸顶灯|1313|
|huayi.light.wy002|华艺照明顶灯通用系列|1996|
|huayi.light.wy006|慧作智能照明(2021版)|4112|
|huayi.light.wy200|慧作良辰吸顶灯(蓝牙Mesh版)|2630|
|huayi.light.wy201|慧作射手星筒灯(蓝牙Mesh)|2658|
|huayi.light.wy202|慧作球泡灯(蓝牙Mesh)|2659|
|huayi.light.wy203|慧作咏方圆筒灯(蓝牙Mesh)|2702|
|huayi.light.wy208|慧作幸运星儿童灯|4446|
|huayi.light.wy211|华艺慧作通用顶灯|7326|
|huayi.light.wy212|华艺智能顶灯|9106|
|huayi.light.wy216|华艺智能筒射灯|13966|
|huayi.light.wy217|华艺智能灯带|13967|
|huayi.light.wy218|华艺智能磁吸灯|13968|
|huayi.light.wyheat|慧作暖阳制热吸顶灯|2466|
|huayi.light.zw131|慧作紫薇星系列吸顶灯|2355|
|huia.light.wy0a01|晖昂智能筒射灯|27179|
|huia.light.wy0a02|晖昂智能灯带|27180|
|huia.light.wy0a03|晖昂智能磁吸灯|27181|
|hwhl.light.hwlwfi|华伟宏亮AI智能灯|34561|
|hwzn.light.wy0a01|喜辉智能吸顶灯|3308|
|hxzm66.light.hxtsd|FANDUNBAO 梵金射灯 Pro|38359|
|hxzm66.light.hxzm23|FANDUNBAO 双色智能灯带|38190|
|hxzm66.light.wy0a01|FANDUNBAO梵金系列智能筒射灯|32962|
|hxzm88.light.wy0a01|钟金华迅智能筒射灯|37368|
|hy2238.light.wy0a01|欧索特智能灯泡mesh2.0|40418|
|hyws.light.zxdd01|GE智能吸顶灯|37993|
|hyws.light.zxdd02|GE智能吸顶灯PRO|38060|
|hyzm.light.wymy1|立范北欧智能灯|1827|
|hyznzm.light.wy0a01|华艺照明智能筒射灯|30306|
|hyznzm.light.wy0a02|华艺智能吸顶灯|30307|
|hyznzm.light.wy0a03|华艺照明智能磁吸灯|39295|
|hzsj.light.wy0a01|山晶特控 情景夜灯Mesh R1版|17072|
|hzsj.light.wy0a02|山晶特控 情景色温灯WiFi版|23164|
|hzsj.light.wy0a03|山晶特控 床头灯WiFi版|32842|
|hzsj.light.wyfa03|山晶特控 氛围床头灯WiFi版|32918|
|hzsj.light.wyra01|山晶特控 氛围夜灯Mesh Q1版|17573|
|hzsj.light.wyra02|山晶特控 氛围灯WiFi版|30086|
|hzx132.light.lddrgb|创智熊AI全彩氛围灯带C1|40960|
|igrow.light.icl101|爱果乐羽光卧室吸顶灯|25105|
|igrow.light.icl102|爱果乐羽光客厅吸顶灯|25602|
|ikea.light.led1536g5|宜家 E14 调温灯|66234|
|ikea.light.led1537r6|宜家 GU10 调温灯|66229|
|ikea.light.led1545g12|宜家 E27 乳白调温灯|66231|
|ikea.light.led1546g12|宜家 E27 透明调温灯|66232|
|ikea.light.led1623g12|宜家 E27 暖白灯|66233|
|ikea.light.led1649c5|宜家 E14 暖白灯|66235|
|ikea.light.led1650r5|宜家 GU10 暖白灯|66230|
|ilin.light.cgd|宜琳橱柜灯|29536|
|imigy.light.ym001|宜美照明吸顶灯（WiFi）|26851|
|inble.light.wy0a01|inSona光因系列吸顶灯|28589|
|inble.light.wy0a02|inSona追光系列光启吸顶灯|37859|
|iot.light.fl02|情景风扇灯|14292|
|iot.light.fl03|情景智能灯pro|14520|
|iot.light.fl04|智能情景风扇灯|14521|
|iot.light.socd01|幻彩灯|11084|
|iot.light.socd03|飞船氛围灯|13661|
|iot.light.socw01|CW冷暖灯|10867|
|isa.light.camsl1|华来AI智能氛围灯带|12205|
|isl.light.rgb01|爱斯兰情景彩光落地灯|37636|
|isl.light.wy0a01|爱斯兰智能灯|5623|
|isl.light.wy0a02|爱斯兰智能Mesh筒射灯|9531|
|isl.light.wy0a03|爱斯兰智能筒射灯|32604|
|jbl123.light.wy0a01|金百丽智能筒射灯|23830|
|jbl123.light.wy0a03|金百丽智能灯带|29795|
|jbl123.light.wy0a04|金百丽智能吊灯|29796|
|jbl123.light.wy0a05|金百丽智能吸顶灯|29797|
|jdjz.light.e1l96|京东京造E1 Pro吸顶灯-L960|35851|
|jdjz.light.e1prow|京东京造E1 Pro吸顶灯-MX480|35230|
|jdjz.light.grf2|京东京造长颈鹿2落地灯|21841|
|jdjz.light.grf2p|京东京造长颈鹿3落地灯|21842|
|jdjz.light.gruw|京东京造 长颈鹿3Ultra LED落地灯|37467|
|jdjz.light.jdjz01|京东京造吸顶灯V1|18527|
|jdjz.light.jdjzu1|京东京造U1吸顶灯|20272|
|jdjz.light.jdjzvg|京东京造Infinity吸顶灯-MX500|33347|
|jdjz.light.jinbu2|京东京造进步台灯2|27676|
|jdjz.light.jzfl01|京东京造 御风者智能风扇灯|36648|
|jdjz.light.lite|京东京造长颈鹿Lite落地灯|21638|
|jdjz.light.lite2|京东京造长颈鹿Lite2落地灯|24640|
|jdjz.light.vgl96|京东京造Infinity吸顶灯-L960|35871|
|jgfy.light.wy0a01|ModaLoft情景Mesh色温吊顶灯UItra S350|32178|
|jhow88.light.wy0a01|捷皓情景智能筒射灯|35660|
|jhzm88.light.wy0a01|JUHAO钜豪智能筒射灯|35488|
|jiadi0.light.gyzndd|光影世家智能灯带（Mesh2.0）|33233|
|jiadi0.light.jwdm20|家的双模式吸顶灯|33299|
|jiadi0.light.jwdm21|家的光影复合吸顶灯|35914|
|jiadi0.light.v8hsm|家的反出光护眼射灯|28161|
|jiadi0.light.v8hsm2|家的智能筒射灯（Mesh2.0）|29422|
|jiadi0.light.v8hsm3|雅点智能筒射灯（Mesh2.0）|29421|
|jiadi0.light.zntsd1|光影世家智能筒射灯（Mesh2.0）|33232|
|jiawen.light.wy0a02|佳文调光调色智能灯|12169|
|jiayu8.light.wy0a01|加裕星光系列筒射灯06|31094|
|jihisi.light.wy0a01|JIHISI智能灯|2744|
|jjz.light.wy0a01|JJZ情景智能灯带|35345|
|jlyhxy.light.wy0a01|JLY智能调光灯带|33318|
|jmkj.light.wy0a01|即米智能情景灯|8464|
|jmls.light.ls001|龙胜智能LED吸顶灯|4190|
|jmzc.light.wy0a01|哲成智能双色筒射灯|31571|
|jmzc.light.zcl03|哲成智能筒射灯|31002|
|jmzc.light.zcl06|哲成智能调光灯带|33799|
|jn0203.light.wy0a01|九头鲸高端智能筒射灯|30912|
|jn0203.light.wy0a02|九头鲸高端智能吸顶灯|36231|
|jpy.light.jpyddm|PHPX智能灯带（Mesh2.0）|37002|
|js1.light.wy0a01|KSIIO智能射灯|31594|
|jsc.light.wydfn1|丹菲诺智能吸顶灯具|1837|
|jsc.light.wyls02|情景蓝牙mesh双色灯|1841|
|jsc.light.wyyt01|研泰智能灯|1838|
|jszm88.light.wy0a01|JUSN智能筒射灯|32383|
|jtjiot.light.wy0a02|捷特佳智能灯带V2|38817|
|jtzm01.light.wy0a01|嘉韬智能筒射灯|37848|
|juduo.light.w00a01|桔朵智能立式护眼灯M1|26242|
|juduo.light.w00a02|桔朵智能立式护眼灯JD1|29303|
|juduo.light.w00a03|桔朵智能立式护眼灯JD2|29310|
|jugel.light.jgltsd|JGL智能筒射灯MESH2.0|33389|
|julun.light.jl0002|julun智能灯(彩光版)|69833|
|julun.light.jlcw|julun智能灯(双色版)|70079|
|julun.light.wyra01|JL溢彩吸顶灯|9077|
|julun.light.wyrf01|JL炫彩风扇灯|9088|
|justdu.light.wyfa01|佳斯度无叶风扇灯|16575|
|jxgc.light.wyxy1|湘裕智能LED吸顶灯|1831|
|jxsoft.light.bump1|晶讯智能灯泡|1665|
|jxzm.light.wy0a03|XMBLT智能灯泡|41197|
|jya.light.sla1|Jya 无线台灯（智能版）|1762|
|jygzm.light.wy0a01|聚有光智能灯带Mesh2.0|35413|
|jymc.light.falmp|智能双色灯(MESH)|10729|
|jymc.light.jmlmp2|智能双色灯|4582|
|jymc.light.lmptjd|JYMC天镜灯(WIFI)|30669|
|jymc.light.pubm20|JYMC智能双色灯带MESH2.0|32807|
|jyp.light.jnym20|JYP低压双色灯带J1|34542|
|jyst.light.wy0a01|鲸云智能情景灯|6553|
|kaili.light.wy0a01|开利智能筒射灯|32059|
|kaili.light.wy0a02|开利智能磁吸灯|37525|
|kdzm.light.kdqpdm|Kodect球泡灯（Mesh2.0)|29497|
|keey.light.qydd|KEEY智能IS灯带|35358|
|keey.light.qywlcd|KEEY智能RGBCW全⾊域灯带|33986|
|keey.light.v8hsm|KEEY智能灯带（Mesh2.0）|28163|
|keey.light.v8hsm1|KEEY 智能筒射灯（Mesh2.0）|28162|
|keey.light.v8hsm4|KEEY智能灯带控制器 （Mesh2.0）|30225|
|kegu.light.wy2a01|KGP智能灯带（Mesh2.0）|30955|
|kinxzo.light.wy0a02|广兴洲智能筒射灯（05系列）|33858|
|kjy.light.kjyddm|KEKINY智能调光调色灯带|28643|
|kjy.light.v8uswd|KEKINY智能双色灯Pro（Mesh2.0）|26888|
|kjy.light.wy0a01|KEKINY筒射灯2.0|26281|
|kjy.light.wy0a03|KEKINY灯带2.0|26508|
|kjy.light.wy0a04|KEKINY全色域灯带|35490|
|kjy.light.wyra01|KEKINYRGBCW灯带|36975|
|klaled.light.qil9x6|琪朗护眼吸顶灯A-L款|37659|
|klaled.light.qila23|琪朗护眼吸顶灯A-S款|37263|
|klaled.light.qila24|琪朗护眼吸顶灯A-M款|37510|
|klaled.light.ql650w|琪朗天空之环母婴灯S41-650|35906|
|klaled.light.ql6a2w|琪朗 SunnyTop 吸顶灯 A2 Max|36654|
|klaled.light.ql6e1w|琪朗光立方吸顶灯E21|35915|
|klaled.light.qlmydw|琪朗天空之环母婴灯S41-850|30184|
|klaled.light.wy0a01|琪朗ALED自然光谱灯|12824|
|klaled.light.wy0a02|琪朗 SunnyTop 吸顶灯|18315|
|klaled.light.wy0a04|琪朗SUNNYTOP吸顶灯升级版|27731|
|klf888.light.wy0a01|客来福智能筒射灯|20621|
|klf888.light.wy0a02|客来福智能灯带|20622|
|klf888.light.wy0a03|客来福智能磁吸灯|20623|
|klgzm.light.wy0a02|采影智能筒射灯|27184|
|klms.light.wy0a01|KLMS智能筒射灯|30821|
|klms.light.wy0a02|KLMS智能磁吸灯|30822|
|klms.light.wy0a03|KLMS智能灯带|36525|
|koey.light.wy0a01|KOEY疆域系列智能筒射灯|12757|
|koey.light.wy0a02|KOEY界系列吸顶灯|16873|
|koey.light.wy0a03|KOEY耀系列磁吸灯|17402|
|koey.light.wy0a04|KOEY天幕系列吸顶灯|21626|
|koey.light.wy0a05|KOEY界PRO系列吸顶灯|27647|
|koey.light.wy0a06|KOEY疆域系列（肤感）筒射灯|27648|
|koey.light.wy0b01|KOEY天幕系列kid吸顶灯|21627|
|kopu.light.wy0a02|KOPU智能灯泡|39605|
|kps.light.kpstsd|可派仕智能筒射灯|33938|
|ksc.light.px1ls|金云智联灯带驱动器X1（PLC版）|80921|
|ksks.light.wy0a01|今上智能筒射灯|17706|
|ksks.light.wy0a02|今上智能线形灯|18167|
|ksks.light.wy0a04|今上智能磁吸灯|18380|
|ksks.light.wy0a05|今上智能筒射灯Pro|27505|
|ksks.light.wy0a06|今上智能线形灯Pro|27513|
|ksks.light.wy0a07|今上智能吸顶灯Pro|33758|
|lab.light.w00a01|老爸评测定制智能控制款大路灯|33584|
|laidun.light.ldddm|LD智能人存灯带(Mesh2.0)|28543|
|laig.light.radar|小徕智存智能灯X1|24881|
|lat888.light.lts26|迅为智能双色调光灯Mesh2.0|26406|
|lb01.light.xylxd|POCOCO 助眠星空灯|28544|
|lczmlc.light.wy0a01|LC智能情景射灯|30248|
|lczmlc.light.wy0a02|领灿智能灯带|33569|
|ldkmj.light.ldkm20|力多科情景柜体灯带|37995|
|ldsiot.light.202888|立达信C2吸顶灯|27812|
|ldsiot.light.202999|立达信C2吸顶灯D50|27811|
|ldsiot.light.d3gg1|立达信萤火虫吊灯|32264|
|ldsiot.light.wy0a01|立达信智能筒射灯|34308|
|ldsiot.light.wy0a02|立达信LED智能灯带|36828|
|ldzn.light.wy0a01|凌动智能筒射灯2.0|25269|
|ldzn.light.wy0a02|凌动智能 磁吸灯2.0|25369|
|ldzn.light.wy0a03|凌动智能 灯带控制器2.0|25370|
|ldzn.light.wy0a04|凌动智能家居吸顶灯|38050|
|ledmy.light.tabled|乐的美智能台灯|34478|
|ledmy.light.wy0a01|乐的美智能筒射灯|36646|
|ledoux.light.nbcxdm|诺邦智能磁吸灯|29285|
|ledoux.light.nbsdm|诺邦智能射灯|29284|
|ledv.light.wy0a01|朗德万斯溪柚客厅系列吸顶灯|3780|
|ledv.light.wy0a02|朗德万斯溪柚卧室系列吸顶灯|3781|
|legui.light.wy0a01|LEGUI宽色域灯带|36679|
|leike.light.wy0a01|雷克智能灯带|37384|
|leike.light.wy0a03|雷克智能筒射灯|37395|
|leimai.light.wy0a01|雷迈智能筒射灯|32543|
|leishi.light.126a1|雷士智能护眼灯饰A1|39125|
|leishi.light.126b1|雷士智能护眼灯饰B1|37839|
|leishi.light.126b2|雷士智能护眼灯饰B2|39355|
|leishi.light.126p|雷士智能护眼灯饰A3|32389|
|leishi.light.126pro|雷士智能灯饰V|26887|
|leishi.light.129p|雷士智能护眼灯饰A2|32394|
|leishi.light.cbfsd|雷士超薄风扇灯|23295|
|leishi.light.cbfsd2|雷士超薄风扇灯N|23780|
|leishi.light.cw0a01|雷士智能筒射灯|5168|
|leishi.light.cwtsd|雷士智能筒射灯Pro|14734|
|leishi.light.eps112|雷士LED智能吸顶灯|1847|
|leishi.light.eps113|雷士满天星LED吸顶灯|2020|
|leishi.light.eps115|雷士智能北欧吸顶灯|3196|
|leishi.light.eps116|雷士智能吊灯|3303|
|leishi.light.eps117|雷士智能射灯|3415|
|leishi.light.eps118|雷士智能LED吸顶灯|4419|
|leishi.light.eps119|雷士智能主辅灯饰|6166|
|leishi.light.eps120|雷士智能LED辅助灯|7474|
|leishi.light.eps121|雷士风扇灯|9535|
|leishi.light.eps122|雷士智能无主灯|10183|
|leishi.light.eps123|雷士智能RGB灯带|10284|
|leishi.light.eps124|雷士智能灯饰max|11243|
|leishi.light.eps125|雷士风扇灯pro|11596|
|leishi.light.eps126|雷士智能灯饰pro|12018|
|leishi.light.eps127|雷士智能led吸顶灯pro|12167|
|leishi.light.eps128|雷士智能灯带V|13174|
|leishi.light.eps129|雷士智能护眼灯饰|15620|
|leishi.light.eps131|雷士智能护眼风扇灯|16216|
|leishi.light.eps132|雷士智能护眼灯饰pro|23865|
|leishi.light.esp114|雷士叠影LED吸顶灯|2644|
|leishi.light.fan01|雷士智能卧室风扇灯|2634|
|leishi.light.fgl|雷士智能灯饰N|26024|
|leishi.light.fsdc3|雷士卧室风扇灯|26340|
|leishi.light.gyb11|雷士智能光源模组（Mesh版）|14838|
|leishi.light.gydtc3|雷士智能光源模组（WiFi版）|16825|
|leishi.light.jhfsd|雷士净化风扇灯|34176|
|leishi.light.lsilm|雷士智能筒射灯 Mesh2.0|31231|
|leishi.light.lsmdld|雷士智能LED护眼落地灯|33419|
|leishi.light.lsrctd|雷士人体存在筒射灯|29489|
|leishi.light.lstd01|雷士智能台灯N1|6921|
|leishi.light.lsxxd|雷士立式学习灯|25688|
|leishi.light.muying|雷士未来光-声光ultra|32284|
|leishi.light.nest|雷士鸟巢LED吸顶灯|2209|
|leishi.light.nvc001|雷士吸顶灯pro|12676|
|leishi.light.nvc002|雷士智能风扇灯pro|12677|
|leishi.light.nvcf01|雷士风扇灯lite|37421|
|leishi.light.rgb001|雷士智能全色域吸顶灯|27218|
|leishi.light.rgb002|雷士未来光Ultra客厅灯|32076|
|leishi.light.rgba01|雷士智能灯泡|2579|
|leishi.light.rgba02|雷士智能彩光灯带|2583|
|leishi.light.rgba03|雷士智能彩光灯泡|2614|
|leishi.light.t1|雷士智能台灯V1|13255|
|leishi.light.tdc3|雷士智能灯带Pro|13623|
|leishi.light.tsdpro|雷士智能筒射灯（Mesh2.0）|26320|
|leishi.light.v11ilw|雷士智能感应平板灯|27296|
|leishi.light.wy0a01|雷士智能球泡|2578|
|leishi.light.wy0a02|雷士智能筒灯|2598|
|leishi.light.wy0a03|雷士智能LED辅灯|2624|
|leishi.light.wy0a04|雷士智能玉米泡|2625|
|leishi.light.wy0a05|雷士智能面板灯|2968|
|leishi.light.wy0a06|雷士智能灯饰|4307|
|leishi.light.wy0a07|雷士智能灯带|4560|
|leishi.light.wy0a08|雷士智能吸顶灯|6083|
|leishi.light.wy0a09|雷士智能光源模组|6084|
|leishi.light.wy0a10|雷士智能吸顶灯pro|10798|
|leishi.light.wy0b01|雷士智能台灯|2582|
|leishi.light.wy0c01|雷士智能吸顶灯（智睿款）|2639|
|leishi.light.wy0c02|雷士智能吸顶灯（智臻款）|2640|
|leishi.light.wyfa02|雷士智能风扇灯（智逸款）|2581|
|leishi.light.wyfa03|雷士智能风扇灯|4448|
|leishi.light.wyfa05|雷士空净清风灯|17384|
|leishi.light.wyfao1|雷士智能风扇灯（智雅款）|2580|
|leishi.light.wyqfd|雷士无叶清风灯|27086|
|leishi.light.wzdc3|雷士智能无主灯pro|16874|
|leishi.light.yying|雷士月影LED吸顶灯|2208|
|lejia.light.33301|情景蓝牙mesh双色灯A|1701|
|lejia.light.wy02|情景mesh色温灯C系列|1702|
|lem.light.lts26|乐亦美智能筒射灯Pro|26698|
|lemesh.light.rgba04|情景电视氛围灯 Pro|18550|
|lemesh.light.w00a01|情景mesh单色灯|4400|
|lemesh.light.w00a02|情景Mesh单色灯V2S系列|17157|
|lemesh.light.w00a03|智能情景护眼落地灯|18484|
|lemesh.light.w00a04|情景智能落地学习灯Pro|20481|
|lemesh.light.w00d01|情景mesh单色灯K系列|2091|
|lemesh.light.w0a01|情景Lemesh人体存在感应灯|22863|
|lemesh.light.wy|情景双色灯WIFI X版|1322|
|lemesh.light.wy02|情景WiFi色温灯C系列|12171|
|lemesh.light.wy0a19|JS智能双色灯|16685|
|lemesh.light.wy0a20|情景Mesh色温灯V2X系列|16697|
|lemesh.light.wy0a21|情景WiFi色温灯TP系列|17266|
|lemesh.light.wy0a22|情景WiFi色温灯Pro|17819|
|lemesh.light.wy0c02|情景mesh色温灯|1910|
|lemesh.light.wy0c03|情景mesh色温灯D系列|1997|
|lemesh.light.wy0c04|情景mesh色温灯K系列|2082|
|lemesh.light.wy0c05|情景mesh色温灯E系列|2351|
|lemesh.light.wy0c07|情景mesh色温灯TM系列|3164|
|lemesh.light.wy0c08|情景mesh色温灯通用系列|3531|
|lemesh.light.wy0c09|情景mesh色温灯V2系列|7136|
|lemesh.light.wy0c12|情景mesh色温灯V2Q系列|12729|
|lemesh.light.wy0c14|情景Mesh色温灯V1S系列|13471|
|lemesh.light.wy0c15|情景Mesh色温灯V2S系列|13525|
|lemesh.light.wy0c17|HT智能灯|15647|
|lemesh.light.wy0c21|情景Mesh色温灯ZS系列|16831|
|lemesh.light.wy0c22|情景Mesh筒射灯KY系列|17081|
|lemesh.light.wy0c23|皇创调色温筒射灯DT1|17672|
|lemesh.light.wy0c24|情景Mesh色温灯V2S Pro|17687|
|lemesh.light.wy0c26|情景Mesh色温灯V2G|18089|
|lemesh.light.wy0d02|情景Lemesh色温灯Ultra|19733|
|lemesh.light.wyfa01|情景智慧风扇灯通用款C3版|12790|
|lemesh.light.wyfa04|情景Lemesh智能风扇灯|24977|
|lemesh.light.wyra01|情景彩光灯Mesh X1版|3399|
|lemesh.light.wyra02|情景Mesh彩光灯V2S|17136|
|lemesh.light.wyrb01|情景mesh氛围色温灯|11618|
|lemesh.light.wyrb02|情景Mesh氛围灯V2S|15918|
|lemi18.light.lemm20|班客全光谱智能吸顶灯|33126|
|lenkei.light.w0ra01|灵鳍智能鱼缸灯|22669|
|lesdn.light.wy0a01|雷施顿智能灯|6732|
|lesdn.light.wy0a02|雷施顿智能筒射灯 Mesh|29508|
|leshi.light.wy0b01|情景WIFI双色灯|2270|
|leshi.light.wy0b03|情景WIFI色温灯|3108|
|leshi.light.wyfa01|情景智慧风扇灯通用款|4835|
|leshi.light.wyfan|情景智慧风扇灯WiFi版|1577|
|leso.light.wy0a03|雷硕智能灯带|33412|
|leso.light.wy0a04|雷硕智能筒射灯|34589|
|lex.light.scxd01|LEXSmart 智能护眼磁吸灯2.0|26719|
|lex.light.scxd02|LEXSmart 全色域霞光健康护眼磁吸灯2.0|37871|
|lex.light.slsx01|LEXSmart 光域大师智能护眼线光灯带2.0|26720|
|lex.light.slsx02|LEXSmart 全色域霞光健康护眼灯带2.0|38537|
|lex.light.stsd01|LEXSmart 智能筒射灯2.0|26721|
|lex.light.stsd02|LEXSmart 全色域霞光健康护眼筒射灯2.0|37870|
|lex.light.sxdd02|LEXSmart 全色域霞光健康护眼吸顶灯2.0|38011|
|lex.light.sxdd03|LEXSmart悬浮柔光智能护眼吸顶灯2.0满血版|40922|
|lex.light.wy0a01|LEXMesh智能双色灯2.0|23215|
|lex.light.wy0a02|LEXMesh 智能护眼线光灯带2.0|26021|
|lgb.light.lt001|巧旺智能灯|37185|
|lh2024.light.wy0a01|LIUHONG留虹照明智能双色灯带|26504|
|lh2024.light.wy0a02|留虹智能筒射灯（Mesh2.0）|32066|
|lh2024.light.wy0a03|留虹智能吸顶灯|35267|
|line.light.frcpbd|方舟鱼人体存在平板灯|23527|
|line.light.frzpbd|方舟鱼人体存在平板灯MP|28269|
|line.light.mrd1|LineHope智能办公灯驱动DR3|7354|
|line.light.mrd2|LineHope智能灯带驱动DR4|7355|
|line.light.mrs1|LineHope智能射灯驱动器DR1|7351|
|line.light.mrs2|LineHope智能射灯驱动器DR2|7352|
|line.light.msd1|LineHope智能射灯DS1|7117|
|line.light.msd1s|LineHope智能射灯DS2|7118|
|line.light.mtd1|LineHope智能筒灯DT1|7116|
|line.light.rcpbd1|LineHope人体存在平板灯|22993|
|line.light.zndy|TATACASA智能灯带|30957|
|linju.light.ljslm2|聆巨智能灯带（Mesh2.0）|25224|
|linju.light.wy0a01|聆巨蓝牙Mesh双色灯|17704|
|linju.light.wy0a02|聆巨智能吸顶灯（mesh2.0）|25377|
|linly.light.wy0a01|LINLY超深度恒流筒射灯|21340|
|linp.light.d1pcw|智能筒射灯（PLC版）|76676|
|linp.light.ld5bcw|linptech智能筒射灯(MESH2.0)|25417|
|linp.light.ld5scw|linptech智能筒射灯|30442|
|linp.light.ld6bcw|linptech人体存在筒射灯|25137|
|linp.light.ldcw01|领普智能筒射灯|9314|
|linp.light.lm1pcw|智能磁吸灯（PLC版）|77329|
|linp.light.lm1pd|智能磁吸吊线灯（PLC版）|79136|
|linp.light.lm1pf|智能磁吸泛光灯（PLC版）|79127|
|linp.light.lm1pg|智能磁吸格栅灯（PLC版）|79142|
|linp.light.lm1ps|智能磁吸射灯（PLC版）|79141|
|linp.light.lmcw01|领普智能磁吸灯|9316|
|linp.light.lp1bc|linptech人体存在平板灯|19653|
|linp.light.lp2bc|linptech人体存在平板灯(MESH2.0)|28229|
|linp.light.ls1pcw|智能灯带（PLC版）|77331|
|linp.light.ls1rgb|智能彩光灯（MESH版）|15677|
|linp.light.lscw01|领普智能灯带|9315|
|linp.light.lx2bcw|linptech人体存在智能灯|23071|
|linp.light.n3bcw|linptech智能筒射灯Lite|37375|
|linp.light.n5bcw|linptech智能筒射灯Pro|34879|
|linp.light.wy0a01|智能筒射灯（MESH版）|17922|
|linrui.light.wy0a01|PHTMTK智能吸顶灯|40937|
|lipro.light.23f4|lipro护眼风扇灯|16893|
|lipro.light.23x1|lipro护眼吸顶灯|15777|
|lipro.light.23x2|lipro护眼客厅吸顶灯|16206|
|lipro.light.23x3|lipro护眼吸顶灯 单色温|16677|
|lipro.light.24a2|lipro护眼餐厅吊灯|20490|
|lipro.light.25a1|lipro护眼餐厅吊灯 Ultra|28225|
|lipro.light.25b1|lipro悦童护眼吸顶灯|25499|
|lipro.light.26x2|lipro悦童护眼吸顶灯 Ultra|33640|
|lipro.light.26x3|lipro护眼吸顶灯|37891|
|lipro.light.26x4|lipro护眼客厅吸顶灯|37892|
|lipro.light.26x7|lipro护眼吸顶灯|38278|
|lipro.light.26x8|lipro护眼吸顶灯 单色温|38332|
|lipro.light.e4b1|lipro护眼面板灯Pro|23336|
|lipro.light.e4z2|lipro柔光落地护眼灯Pro|22708|
|lipro.light.e4z3|lipro柔光落地护眼灯Max|24029|
|lipro.light.r3g2|lipro护眼磁吸轨道灯|18266|
|lipro.light.r3g3|lipro护眼磁吸轨道灯 单色温|19080|
|lipro.light.r3p3|lipro护眼筒射灯|18110|
|lipro.light.r3p5|lipro护眼灯带 单色温|19219|
|lipro.light.r4t2|lipro护眼明装筒射灯|24462|
|lishwy.light.lxznd2|丽炫智能灯带V9（Mesh2.0）|29098|
|live.light.fs901|Yeelight逸扬直流变频风扇吊灯C900SE|10616|
|live.light.fsl001|FSL智能风扇灯系列|18717|
|lj2018.light.wy0a01|LIJIE智能灯带|32927|
|lj2018.light.wy0a04|LIJIE智能筒射灯|39359|
|ljia.light.wy0a01|LJIA智能筒射灯|36298|
|lkzm.light.wy0a01|雷卡之星智能筒射灯|32388|
|lkzm.light.wy0a02|雷卡之星智能情景灯带|33260|
|lkzm.light.wy0a03|雷卡之星智能磁吸灯|33447|
|lman.light.wy0a01|朗漫智能双色温氛围灯带|37349|
|lmds.light.wy0a01|乐盟照明客厅吸顶灯|3715|
|lmds.light.wy0a02|乐盟照明卧室吸顶灯|3716|
|lndq.light.wy0a01|LUNO绿能米家智能灯|2743|
|login.light.wy0a01|BL智能吸顶灯|35311|
|login.light.wyfa01|BL智能风扇灯|35351|
|login.light.wyrb01|BL智能吸顶灯F|39259|
|longs.light.los420|龙胜/AI全色域幻彩节律吸顶灯-42CM|31836|
|longs.light.los560|龙胜/AI全色域幻彩节律吸顶灯-56CM|31837|
|longs.light.losque|龙胜/AI全色域幻彩节律吸顶灯-长方|31855|
|longs.light.lsdd01|龙胜智能灯带|20171|
|longs.light.lsfsd1|龙胜智能护眼风扇灯-F1|40237|
|longs.light.lsrgbd|龙胜/AI全色域幻彩智能灯带（Mesh2.0）|39562|
|longs.light.lssd|龙胜智能射灯S3（Mesh2.0）|35475|
|longs.light.lstd|龙胜智能筒灯T2（Mesh2.0）|35474|
|longs.light.lsts01|龙胜智能筒射灯|20169|
|longs.light.lsts02|龙胜智能筒射灯 Mesh2.0|33079|
|longs.light.lsxdd1|龙胜智能护眼吸顶灯-X1-长方|39288|
|longs.light.lsxdd2|龙胜智能护眼吸顶灯-X1-小圆|40230|
|lp0000.light.v8hsm|蓝宝利 双色智能灯带控制器（Mesh2.0）|31465|
|lrn.light.wya01|LRN双色调光驱动|15893|
|lsds.light.wy0a01|胜信智能灯|2107|
|lss.light.wy0a01|LEISHISHAN智慧筒射灯Plus|29605|
|lss.light.wy0a02|LEISHISHAN智慧吸顶灯Plus|32980|
|lss.light.wyfa01|LEISHISHAN智能风扇灯V1|37444|
|ltdzsw.light.wylg1|利歌灯饰|1828|
|lumi.light.acn003|Aqara 吸顶灯 L1-350|72885|
|lumi.light.acn014|Aqara LED灯泡 T1 (可调色温)|73414|
|lumi.light.acn033|Aqara 吸顶灯|78230|
|lumi.light.aqcn02|Aqara LED灯泡（可调色温）|670|
|lumi.light.cwopcn01|吸顶灯MX960(可调色温)|66833|
|lumi.light.cwopcn02|吸顶灯MX650(可调色温)|66832|
|lumi.light.cwopcn03|吸顶灯MX480(可调色温)|66831|
|luno.light.wy0a02|SALY束璨健康光筒射灯|31459|
|luno.light.wy0a03|SALY束璨健康光吸顶灯|31528|
|luoban.light.wy0a01|LB智能筒射灯|37189|
|luoman.light.lmcxd|罗曼时光智能磁吸灯（Mesh2.0）|29492|
|luoman.light.lmdd1|罗曼时光智能灯带Ultra|40256|
|luoman.light.lmddm|罗曼时光智能灯带（Mesh2.0）|28929|
|luoman.light.lmtsd1|罗曼时光智能筒射灯Ultra|40081|
|luoman.light.v9hsm|罗曼时光智能筒射灯（Mesh2.0）|28264|
|luse.light.wy0a01|金郃光智能吸顶灯|30529|
|lvgmbh.light.lvcw01|朗德万斯智能客厅灯|36414|
|lvgmbh.light.lvcw03|朗德万斯智能卧室灯|36423|
|lvgmbh.light.lvcxd|朗德万斯智能磁吸灯|39290|
|lvgmbh.light.lvdd01|朗德万斯灯带(Mesh2.0)|38302|
|lvgmbh.light.lvts01|朗德万斯筒射灯(Mesh2.0)|38301|
|lvgmbh.light.lvxdd|朗德万斯吸顶灯LY|38602|
|lvl.light.wy0a01|莱维超薄智能吸顶灯|8222|
|lxun.light.znd02|LX色温灯mesh版|15451|
|lxun.light.znd04|LX彩光灯mesh版|16255|
|lymax.light.jfzndm|LYMAX智能显示器挂灯(Mesh2.0)|33434|
|lymax.light.lmshyd|LYMAX智能护眼台灯(WiFi)|29351|
|lyzm.light.wy0a01|乐沿智能筒射灯|35263|
|lzmesh.light.wy0a01|朗尊MESH智能筒射灯|23809|
|lzmesh.light.wy0a02|朗尊MESH2.0智能控制情景灯带|25108|
|lzmesh.light.wy0a03|朗尊蓝牙MESH2.0筒射灯|34194|
|magao.light.wy0a01|MG智能灯（蓝牙Mesh版）|7387|
|maidun.light.mdtsdm|迈顿智能射灯(mesh2.0)|37788|
|manew.light.wy0a01|思码光扶光双色温灯带|26855|
|manew.light.wy0a02|思码光扶光智能筒射灯|26856|
|manew.light.wy0a03|思码光扶光D智能射灯|29254|
|manew.light.wyra01|思码光云霞四合一淡彩灯带|27258|
|manew.light.wyra02|思码光云霞电视同步灯带|28318|
|manew.light.wyra03|思码光云霞淡彩落地灯|28319|
|manew.light.wyra06|思码光云霞淡彩云境灯|31483|
|manew.light.wyra07|思码光云霞淡彩灯带M3|36197|
|manew.light.wyra10|思码光云霞淡彩灯带L1|38106|
|mcolor.light.wy0a01|MCOLOR智能筒射灯|33376|
|me3362.light.wy0a01|朗勃司智能筒射灯|39494|
|mgzn.light.mgdd02|MG智能LED线条灯|10632|
|mgzn.light.mggs01|MG智能磁吸灯|10633|
|mgzn.light.mgmz01|MG智能明装筒射灯|10631|
|mgzn.light.mgzk|MG智能筒射灯|11197|
|mgzn.light.wy0a01|C09MG智能灯|9094|
|miir.light.ir01|灯泡遥控|65716|
|mijia.light.group1|智能灯组|68284|
|mijia.light.group2|智能灯组|68285|
|mijia.light.group3|智能灯组|68286|
|mijia.light.group4|智能灯组|68287|
|mijia.light.group5|智能灯组|70912|
|mioron.light.wy0a01|妙朗智能筒射灯|26828|
|miot.light.lg1|test_light|19709|
|mizhi.light.dmtsdm|DIMAN智能筒射灯（Mesh2.0）|34122|
|mj188.light.wy0a01|星悦亮智能筒射灯|34341|
|mjkj.light.jmdd|即米宽色温灯带（Mesh 2.0）|35468|
|mjkj.light.plc001|BUBA智能筒射灯(PLC)|82150|
|mjkj.light.plc002|BUBA智能线性灯(PLC)|82210|
|mjkj.light.wy0a01|即米智能灯|12540|
|mjkj.light.wy0a02|即米智能磁吸灯|13010|
|mjkj.light.wy0a03|即米智能线性灯|13025|
|mjkj.light.wy0a04|即米筒射灯2.0|23281|
|mjkj.light.wy0a05|即米智能线性灯2.0|23282|
|mjkj.light.wy0a07|即米筒射灯Ultra|29485|
|mjkj.light.wy0a08|即米智能装饰吸顶灯|36303|
|mjx.light.wy0a01|名景芯 智能筒射灯 Ultra|37369|
|mjx.light.wy0a02|名景芯 智能家居吸顶灯 Ultra|37522|
|mjx.light.wy0a03|名景芯 智能客厅吸顶灯 Ultra|37849|
|mjzm.light.6030|月影智能护眼灯air|26706|
|mjzm.light.ceilin|月影自然光护眼灯|19819|
|mjzm.light.magnet|月影护眼磁吸灯|19702|
|mjzm.light.mf7502|月影智能照明吸顶灯pro|25189|
|mjzm.light.v1|月影护眼筒射灯|19222|
|mjzm.light.wy0a01|月影智能吸顶灯|11955|
|mjzm.light.wy0a02|月影智能吊灯|11957|
|mjzm.light.wy0a03|希尔顿智能吸顶灯|12224|
|mjzm.light.wy0a04|希尔顿智能吊灯|12225|
|mjzm.light.wyfa01|月影智能风扇灯|15395|
|mjzm.light.yyfy01|月影自然光环境护眼灯|19949|
|mjzm.light.yyfy02|月影自然光变频风扇灯|21069|
|mkit.light.mkwldd|ABKY智能彩光灯带（Mesh2.0）|35503|
|mkit.light.wyra01|音乐律动焕彩灯带|12922|
|mls.light.mls001|木林森智能照明吸顶灯1|4475|
|mls.light.mls002|木林森智能照明吸顶灯2|4476|
|mls.light.mls003|木林森智能照明吸顶灯3|4622|
|mlszm.light.mlsdd|MLS星漫智能灯带|38458|
|mlszm.light.mlsts2|MLS星火智能筒射灯|38972|
|mlszm.light.mlsts3|MLS凌霄T01智能筒射灯|39098|
|mlszm.light.mlsts4|MLS凌霄T02智能筒射灯|39099|
|mlszm.light.mlstsd|MLS星空智能筒射灯|38457|
|mlszm.light.wy0a01|木林森吸顶灯|38894|
|mly.light.wy0a01|魔力云智能灯|6030|
|mnc.light.wy0a01|米尼智能灯|4161|
|mpkj.light.wy0a01|XINHUI智能节律Mesh2.0筒射灯|25972|
|mpkj.light.wy0a02|XINHUI智能节律Mesh2.0磁吸灯|25974|
|mson.light.ms000|情景MESH双色调光灯 S1|12918|
|mson.light.ms005|情景WIFI双色调光灯 S1|15487|
|mson.light.ms006|情景MESH双色调光灯 S2|17890|
|murong.light.mrk004|慕容柯智能灯|16909|
|murong.light.mrk007|慕容柯节律灯Mesh2.0|28562|
|murong.light.mrk010|慕容柯人存小夜灯Mesh2.0|34179|
|mvs.light.wy0a01|智能筒射灯Mesh版|17964|
|mvs.light.wy0a02|智能灯带Mesh版|17970|
|mvs.light.wy0a03|智能磁吸灯Mesh版|17972|
|mw2025.light.hlwdd|海莱威智能灯带(Mesh2.0)|38340|
|mxg888.light.mxgts1|萌小光智能筒射灯Ultra|40635|
|mxg888.light.wy0a01|萌小光智能筒射灯|33448|
|mxsh88.light.mxshfp|小战智能LED升降风扇灯|39255|
|mxsw.light.fsmrgb|满星思维S1-AI淡彩氛围流水灯带|40503|
|mxsw.light.mxswdd|满星思维智能灯带(满血版mesh2.0)|38408|
|mxsw.light.mxswts|满星思维智能筒射灯(满血版mesh2.0)|38405|
|mxsw.light.wy0a01|满星思维智能磁吸灯 mesh2.0|23729|
|mxsw.light.wy0a02|满星思维智能灯带 mesh2.0|23736|
|mxsw.light.wy0a03|满星思维智能筒射灯 mesh2.0|23737|
|mxsw.light.wy0a04|满星思维智能吸顶灯mesh2.0|33641|
|mxsw.light.wyra01|满星思维RGBCW幻彩灯带|35188|
|mz1.light.wy0a01|猫泽M9智能筒射灯（Mesh2.0）|31409|
|mzgd.light.wy0a02|美的双色智能吸顶灯|26610|
|nbxh.light.kltsdm|JOCO智能筒射灯（Mesh2.0）|28930|
|nbxh.light.xhdd|JOCO巨省电智能灯带（低功耗Mesh2.0）|39955|
|nmks.light.wy0a02|nameeks智能筒射灯Ultra|26946|
|nmks.light.wy0a03|nameeks智能灯带|26947|
|nmks.light.wy0a04|nameeks智能吸顶灯|26948|
|nmks.light.wy0a05|nameeks智能磁吸灯|26949|
|nmt.light.wy0a01|双色智能灯|17862|
|nnleaf.light.glbulp|Nanoleaf Shapes 双模版|4126|
|nnleaf.light.nl52|Nanoleaf 木纹奇光板|73977|
|nnleaf.light.nl59|Nanoleaf 智能星座灯|73973|
|nnleaf.light.nl64|Nanoleaf 积木天空灯|80210|
|nnleaf.light.nl81|Nanoleaf 积木奇光板|83494|
|nnleaf.light.sqfx01|方塔希EXPO智能展陈盒|78004|
|nnleaf.light.strips|Nanoleaf智能灯带|69900|
|nnleaf.light.ulp|Nanoleaf Shapes|68011|
|noc.light.ok33|HAPPY NOCNOC圆形吸顶灯-新|26421|
|noc.light.ok34|HAPPY NOCNOC 方形吸顶灯|27481|
|noc196.light.mdctd9|米典智能床头健康灯|68156|
|noc196.light.mdyctd|米典零蓝光音乐氛围灯|71176|
|nork.light.nokbv2|诺克照明吸顶灯|33416|
|nork.light.wy0a01|诺克照明智能吊灯|29267|
|nork.light.wy0a02|诺克照明智能吸顶灯|31853|
|nork.light.wy0a03|诺克照明智能壁灯|31852|
|nork.light.wyrb01|诺克照明氛围吸顶灯|32369|
|npu.light.npu001|NPU耐普照明智能灯|9540|
|ntgd.light.nttsd1|光艺狮智能筒射灯（Mesh2.0）|38325|
|nuojia.light.ljfsdm|LJ智能风扇灯（Mesh2.0）|37716|
|nvcsmt.light.bas201|雷士智能筒射灯（专业版）|7763|
|nvcsmt.light.bas202|雷士智能筒射灯（双色款TB）|12281|
|nvcsmt.light.bas203|雷士智能筒射灯（plus）|13075|
|nvcsmt.light.bas204|雷士智能射灯M90|29893|
|nvcsmt.light.bas205|雷士双色筒射灯Pro|32905|
|nvcsmt.light.bas206|雷士智能筒射灯L90|32906|
|nvcsmt.light.bas208|雷士智能筒射灯M01Pro|36984|
|nvcsmt.light.bcs201|雷士智能磁吸轨道灯|14979|
|nvcsmt.light.bcs202|雷士智能磁吸导轨线性灯|32908|
|nvcsmt.light.bcs203|雷士智能磁吸导轨格栅灯|32965|
|nvcsmt.light.bcs204|雷士智能磁吸导轨洗墙灯|32967|
|nvcsmt.light.bds101|雷士智能灯带（单调光）|16042|
|nvcsmt.light.bds201|雷士智能灯带（双色款TB）|12282|
|nvcsmt.light.bns203|雷士智能明装格栅灯|36958|
|nvcsmt.light.bns204|雷士智能嵌入式格栅灯|36959|
|nvcsmt.light.bss201|雷士智能磁吸导轨射灯|32907|
|nvcsmt.light.bts101|雷士智能筒射灯（单调光）|16041|
|nvcsmt.light.bts202|雷士智能筒射灯（M系列）|27821|
|nvcsmt.light.dbs202|雷士智能双色温灯带Pro|32904|
|nvcsmt.light.dbs203|雷士智能双色温灯带|32903|
|nvcsmt.light.ffs101|雷士皓彩智能风扇灯|28203|
|nvcsmt.light.ffs201|雷士智能无叶风扇灯|24273|
|nvcsmt.light.ffs202|雷士智能无叶风扇灯Pro|36285|
|nvcsmt.light.fxj203|雷士家居智能吸顶灯 V1|33580|
|nvcsmt.light.fxj204|雷士家居智能吸顶灯 V2|33581|
|nvcsmt.light.fzj501|雷士家居智能淡彩光灯饰|34687|
|nvcsmt.light.wxd101|雷士光屿吸顶灯|31920|
|nvcsmt.light.wxj301|雷士家居智能吸顶灯（专业版）|9467|
|nvcsmt.light.wxs201|雷士家居智能吸顶灯（单主光卧室）|36960|
|nvcsmt.light.wxs202|雷士家居智能吸顶灯（单主光客厅）|36961|
|nvcsmt.light.wxs301|雷士家居智能吸顶灯（主辅光卧室）|36962|
|nvcsmt.light.wxs302|雷士家居智能吸顶灯（主辅光客厅）|36982|
|nvcsmt.light.wzj201|雷士枝型灯|7779|
|nvcsmt.light.wzj202|雷士吊灯PRO|36740|
|nvcsmt.light.wzs101|雷士浮光餐吊灯|32752|
|nwxyd.light.nf01|纽尔智能落地灯NF01|31930|
|odds.light.wy0a01|展秀水晶之恋智能灯|2975|
|odeku.light.hgswdm|ODEKU线条灯带|33548|
|oeco.light.a2803|RippMesh-CW智能桥接灯|21554|
|oml.light.fwlig|欧曼SHINE动态氛围灯带|37960|
|oml.light.omlatv|欧曼SHINE全彩氛围落地灯|38087|
|oml.light.w00a01|欧曼智能人存感应平板灯|34908|
|oml.light.w00a02|欧曼智能人存感应射灯|34916|
|oml.light.w00a03|欧曼智能人存感应筒灯|34941|
|oml.light.wy0a01|OML智能双色灯带2.0|24064|
|oml.light.wy0a02|OML智能双色射灯|26860|
|oml.light.wy0a03|欧曼智能射灯Lite|34803|
|oml.light.wyra01|OML智能五色灯带2.0|24066|
|oml.light.wyra03|欧曼智能全彩筒射灯|27878|
|oml.light.wyra04|OML智能氛围吸顶灯（流光溢彩系列）|27985|
|oot.light.ottsdm|OUTA智能筒射灯（Mesh2.0）|37694|
|oppein.light.wy0a01|欧派-M5智能双色温射灯|39061|
|oppein.light.wy0a02|欧派-M5智能RGB射灯|39063|
|opple.light.000510|OPPLE 博睿 Pro台灯|82947|
|opple.light.000512|OPPLE 元睿2 Plus台灯|82971|
|opple.light.000ad1|OPPLE CX20磁吸导轨灯|82737|
|opple.light.290102|OPPLE 智能吸顶灯|82739|
|opple.light.2906d1|OPPLE  智能主辅光灯|82570|
|opple.light.2907d2|OPPLE  天境吸顶灯|82700|
|opple.light.2d01d1|OPPLE  双色灯带|82736|
|opple.light.2d01d2|OPPLE  筒射灯|82744|
|opple.light.2d02d1|OPPLE  单色灯带|82735|
|opple.light.2d0602|OPPLE 悦瞳L3 Pro落地灯|82967|
|opple.light.2d07c2|OPPLE SDL灯带|82568|
|opple.light.2d07d6|OPPLE SDL筒射灯|83316|
|opple.light.2e01d1|OPPLE CX15磁吸导轨灯|82738|
|opple.light.3plus|OPPLE米悦 Pro台灯|24995|
|opple.light.510101|OPPLE 智能灯组|83094|
|opple.light.510702|OPPLE SDL智能灯组|83107|
|opple.light.510703|OPPLE SDL吸顶灯组|83104|
|opple.light.barelp|欧普智能灯板 Mode A|3661|
|opple.light.brpro|OPPLE 博悦 Pro台灯|31716|
|opple.light.brs|OPPLE 博睿S台灯|31389|
|opple.light.bydceiling|OPPLE欧普照明智能灯|67249|
|opple.light.bysd|OPPLE冰雨射灯|10692|
|opple.light.bytd|OPPLE冰雨筒灯|10691|
|opple.light.dcfan|OPPLE 直流变频风扇灯|4660|
|opple.light.dcfan2|欧普风扇灯|14079|
|opple.light.dcfan4|欧普风扇灯pro|17214|
|opple.light.dcfan5|欧普风扇灯|20207|
|opple.light.dcfan8|欧普风扇灯pro|21422|
|opple.light.dcfan9|欧普风扇灯proII|22209|
|opple.light.fan10|欧普升降风扇灯|38117|
|opple.light.fanlight|OPPLE 智能风扇灯|67534|
|opple.light.gy|OPPLE 欧普照明智能灯 PRO|12551|
|opple.light.jytd|OPPLE京悦 台灯|36449|
|opple.light.lgtstr|欧普智能灯带 Mode A|3187|
|opple.light.lifa01|欧普装饰风扇灯|26183|
|opple.light.mg3td|OPPLE米格3Pro台灯|24958|
|opple.light.mgtd|OPPLE米格2Pro台灯|10689|
|opple.light.moat|OPPLE 欧普照明智能灯 S|15364|
|opple.light.moath|OPPLE 欧普照明智能灯 S|31520|
|opple.light.moats|OPPLE 欧普照明智能灯 S|19049|
|opple.light.opmxsd|OPPLE 明炫Ⅱ 射灯|21384|
|opple.light.optd|OPPLE智能筒射灯|35494|
|opple.light.opxddw|欧普照明灵晖吸顶灯|35733|
|opple.light.qling|OPPLE 厨卫灯|13900|
|opple.light.tabcol|欧普智能台灯 Mode B|2827|
|opple.light.tabcw|欧普智能台灯 Mode C|3247|
|opple.light.tablgt|欧普智能台灯 Mode A|2570|
|opple.light.xxd|OPPLE 欧普照明智能灯 S|12552|
|opple.light.yrtd|OPPLE元睿2Pro台灯|10690|
|opple.light.yy3p|OPPLE元悦3PLUS台灯|29154|
|opple.light.yytd|OPPLE元悦2Pro台灯|10688|
|orrgi.light.w00a03|启源护眼灯|20538|
|orrgi.light.wy0a01|启源双色灯|7878|
|orrgi.light.wy0a02|启源全域护眼吸顶灯|34006|
|ougn.light.wy0a01|欧歌诺智能灯|2106|
|pak.light.541124|三雄极光照明灯具|19224|
|pak.light.ds01|三雄极光Pak 人存感应智能筒灯|31301|
|pak.light.ds02|三雄极光Pak人存感应智能射灯|31352|
|pak.light.fan01|三雄智能风扇灯|10869|
|pak.light.fan03|三雄极光隐形风扇灯|16219|
|pak.light.fan04|三雄极光Pak 御风智能升降环抱风扇灯|29687|
|pak.light.pak002|三雄极光Pak 智能吊灯|4111|
|pak.light.pak005|三雄极光照明家居智能吸顶灯|4460|
|pak.light.pak006|三雄极光智能灯泡|5270|
|pak.light.pak007|三雄极光智能照明吸顶灯|6986|
|pak.light.pak01|三雄极光照明智能吸顶灯|3628|
|pak.light.pak08|三雄极光智能家居吸顶灯|7876|
|pak.light.pak10|三雄极光Pak智能吊灯|7877|
|pak.light.pak12|三雄极光智能射灯|9564|
|pak.light.pak13|三雄极光Pak智能灯饰|12783|
|pak.light.pak14|三雄极光Pak智能家居灯饰|12785|
|pak.light.pak15|三雄极光Pak智能灯具|15078|
|pak.light.pak17|三雄极光Pak 吸顶灯MAX|22695|
|pak.light.pak18|三雄极光Pak 智能全色域吸顶灯|31159|
|pak.light.pak20|Pak天域声光伴眠吸顶灯（芒彩版）|32337|
|pak.light.pak21|Pak天域声光伴眠吸顶灯（天镜版）|32338|
|pak.light.pak22|三雄极光智能光健康灯|36422|
|pak.light.pak23|三雄极光智能光健康灯Pro|36424|
|pak.light.pak24|三雄极光全色域音乐灯玥语|36425|
|pak.light.pak25|三雄极光风扇灯|39443|
|pak.light.pakcw1|三雄极光PAK智能人存厨卫灯|32946|
|pak.light.pakcw3|三雄极光Pak 智能人存射灯 悦影|39101|
|pak.light.pakcw4|三雄极光Pak 智能人存筒灯 悦影|39102|
|pak.light.rbg001|三雄极光Pak 智能灯带 光影RGBCW|36920|
|pak.light.v8uswd|三雄极光Pak 智能磁吸灯|25293|
|pak.light.w00a01|三雄极光Pak AI大立灯|29962|
|pak.light.wy0a03|三雄极光Pak 智能射灯|23284|
|pak.light.wy0a05|三雄极光Pak 智能灯带|23314|
|pak.light.wy0a08|三雄极光Pak 智能磁吸灯2.0|31601|
|pak.light.wy0a10|三雄极光Pak 智能射灯2.0|36845|
|pak.light.wy0a11|三雄极光Pak 智能筒灯2.0|36846|
|pak.light.wy0a14|三雄极光Pak 智能灯带 光影双色|36849|
|pbm.light.accct1|柏曼智能双色灯|9322|
|pbm.light.bmsld|柏曼智能节律灯Plus|29521|
|pbm.light.cbfxwl|柏曼日光Air吸顶灯 方形|35742|
|pbm.light.cbyxwl|柏曼日光Air吸顶灯 大款|35741|
|pbm.light.fancl1|柏曼智能无叶风扇灯V1|25742|
|pbm.light.fdyxwl|柏曼日光Air吸顶灯 中款|35740|
|pbm.light.lfs001|柏曼智能风扇灯|26537|
|pbm.light.lfs004|柏曼羽翼风扇灯|39838|
|pbm.light.pcdct5|柏曼熙光餐吊灯1.6m|36436|
|pbm.light.pdst4|柏曼熙光餐吊灯1.2m|33240|
|pbm.light.pdxst3|柏曼智能节律灯 Pro Max|31042|
|pbm.light.plst2m|柏曼骑士 Z Pro 智能大路灯|25876|
|pbm.light.plst2p|柏曼骑士 Z Max 智能大路灯|25875|
|pbm.light.pm07d|柏曼智能调光灯-B1|19137|
|pbm.light.pm07s|柏曼智能节律灯- B1|19134|
|pbm.light.pmt054|柏曼智能台地灯-HCL|21409|
|pbm.light.ptsd1b|柏曼智能调光灯-B2|25885|
|pbm.light.ptst1b|柏曼智能节律灯- B2|25886|
|pbm.light.pxd5v2|柏曼智能节律灯 Pro|27554|
|pbm.light.td001|柏曼灵动光台灯|25228|
|pbm.light.wy0a01|柏曼嵌入磁吸长条灯|25746|
|philips.light.aibed|米家伴睡唤醒灯|4105|
|philips.light.bceil|飞利浦智睿吸顶灯 简约版 客厅80W|6034|
|philips.light.bceil1|飞利浦智睿吸顶灯 简约版 卧室40W|6035|
|philips.light.bceil2|飞利浦智睿吸顶灯 简约版 卧室28W|6036|
|philips.light.bceiling1|飞利浦智睿吸顶灯 简约版 卧室40W|1162|
|philips.light.bceiling2|飞利浦智睿吸顶灯 简约版 卧室28W|1163|
|philips.light.blue|飞利浦蓝天灯|6449|
|philips.light.blue1|飞利浦落霞灯|13862|
|philips.light.boc1|飞利浦智奕吸顶灯 流年G2 客厅80W|4682|
|philips.light.boc2|飞利浦智奕吸顶灯 流年G2 卧室40W|4683|
|philips.light.boc3|飞利浦智奕吸顶灯 流年G2 卧室28W|4684|
|philips.light.candle|飞利浦智睿蜡烛灯泡 小螺口磨砂版|624|
|philips.light.candle2|飞利浦智睿蜡烛灯泡 小螺口水晶版|682|
|philips.light.cbulb|米家飞利浦彩光灯泡|66283|
|philips.light.ce130c|飞利浦品逸吸顶灯 130W|29322|
|philips.light.ce130x|飞利浦盈乐吸顶灯 130W|29319|
|philips.light.ce13zx|飞利浦知白吸顶灯 130W|29451|
|philips.light.ce36c|飞利浦星环吸顶灯 36W|29325|
|philips.light.ce36x|飞利浦盈乐吸顶灯 36W|29321|
|philips.light.ce48c|飞利浦星环吸顶灯 48W|29324|
|philips.light.ce48x|飞利浦知白吸顶灯 48W|29320|
|philips.light.ce80c|飞利浦星环吸顶灯 80W|29323|
|philips.light.ce80yc|飞利浦盈乐吸顶灯 80W|29453|
|philips.light.ceil33|米家飞利浦卧室吸顶灯 典雅版|2291|
|philips.light.ceilfi|飞利浦智能吸顶灯|22025|
|philips.light.ceiling|飞利浦智睿吸顶灯|393|
|philips.light.ceilp|米家飞利浦客厅吸顶灯 典雅版|2263|
|philips.light.ceilz|飞利浦智睿吸顶灯 简约版G2 小卧室|12086|
|philips.light.ceilz1|飞利浦智睿吸顶灯 简约版G2 大卧室|12087|
|philips.light.ceilz2|飞利浦智睿吸顶灯 简约版G2 小客厅|12088|
|philips.light.ceilz3|飞利浦智睿吸顶灯 简约版G2 大客厅|12155|
|philips.light.dlight|智睿LED筒灯 调光版|68359|
|philips.light.downlight|飞利浦智睿筒灯|488|
|philips.light.eceil|飞利浦安瑞系列-C9客厅吸顶灯120W|25446|
|philips.light.ecl01|飞利浦安瑞系列-C9卧室吸顶灯55W|25831|
|philips.light.epan|飞利浦安瑞系列-C9面板灯24W|25447|
|philips.light.fl|飞利浦F9 Lite落地灯|17446|
|philips.light.flat|飞利浦智睿跌倒检测面板灯|14299|
|philips.light.lite|米家智能台灯Lite|4944|
|philips.light.lnblight1|飞利浦智奕吸顶灯 流年版 卧室40W|1422|
|philips.light.lnblight2|飞利浦智奕吸顶灯 流年版 卧室28W|1421|
|philips.light.lnlrlight|飞利浦智奕吸顶灯 流年版 客厅80W|1423|
|philips.light.lrceiling|飞利浦智睿吸顶灯 简约版 客厅80W|1073|
|philips.light.lying1|飞利浦智睿吸顶灯 流萤版G2 大客厅|13594|
|philips.light.lying2|飞利浦智睿吸顶灯 流萤版G2 小客厅|13595|
|philips.light.lying3|飞利浦智睿吸顶灯 流萤版G2 大卧室|13596|
|philips.light.lying4|飞利浦智睿吸顶灯 流萤版G2 小卧室|13597|
|philips.light.mceil|智睿吸顶灯 北欧款 客厅80W|2027|
|philips.light.mceilm|智睿吸顶灯 北欧款 卧室40W|2104|
|philips.light.mceils|智睿吸顶灯 北欧款 卧室28W|2105|
|philips.light.mm1|飞利浦智睿吸顶灯 魅影 客厅80W|4994|
|philips.light.mm2|飞利浦智睿吸顶灯 魅影 卧室40W|4995|
|philips.light.mm3|飞利浦智睿吸顶灯 魅影 卧室28W|4996|
|philips.light.mono1|飞利浦智睿台灯|55|
|philips.light.nlight|米家飞利浦蓝牙夜灯|989|
|philips.light.obceil|智睿吸顶灯 黑曜石 客厅80W|2960|
|philips.light.obceim|智睿吸顶灯 黑曜石 卧室40W|2961|
|philips.light.obceis|智睿吸顶灯 黑曜石 卧室28W|2962|
|philips.light.pceil|米家吸顶灯Pro 客厅版|9324|
|philips.light.pceil1|飞利浦碳索环保吊灯|24224|
|philips.light.pceilb|米家吸顶灯Pro 卧室版|9753|
|philips.light.piano|米家智能钢琴灯|9474|
|philips.light.rwread|米家飞利浦读写台灯|66742|
|philips.light.sceil|智睿吸顶灯 流萤 客厅80W|2620|
|philips.light.sceilm|智睿吸顶灯 流萤 卧室40W|2621|
|philips.light.sceils|智睿吸顶灯 流萤 卧室28W|2622|
|philips.light.sread2|米家飞利浦台灯2S|66615|
|philips.light.sread3|米家飞利浦台灯3|69491|
|philips.light.sread4|智睿读写台灯 Wi-Fi版|71315|
|philips.light.sread6|飞利浦智睿台灯2S|73512|
|philips.light.sread8|飞利浦智秀台灯|74366|
|philips.light.sread9|米家台灯Pro 读写版|9380|
|philips.light.street|飞利浦F9落地灯|15457|
|philips.light.strip2|智睿彩光灯带|69258|
|philips.light.strip3|米家追光氛围灯带|4729|
|philips.light.virtual|飞利浦智睿系列灯组|462|
|philips.light.xzceil|智睿吸顶灯 星钻 客厅80W|2957|
|philips.light.xzceim|智睿吸顶灯 星钻 卧室40W|2958|
|philips.light.xzceis|智睿吸顶灯 星钻 卧室28W|2959|
|philips.light.yb1|飞利浦智睿吸顶灯 月白 客厅80W|4991|
|philips.light.yb2|飞利浦智睿吸顶灯 月白 卧室40W|4992|
|philips.light.yb3|飞利浦智睿吸顶灯 月白 卧室28W|4993|
|philips.light.zyceiling|飞利浦智奕吸顶灯|559|
|philips.light.zysread|飞利浦智奕台灯|626|
|philips.light.zystrip|飞利浦智奕灯带|659|
|pls.light.wy0a01|工匠智能筒射灯（Mesh2.0）|33078|
|pmfbj.light.7s203s|松下筒射灯|13928|
|pmfbj.light.820580|松下智能恒压DC灯带|30207|
|pmfbj.light.9z252s|松下智能筒射灯|24189|
|pmfbj.light.ls5000|松下餐吊灯|15708|
|pmfbj.light.lt0668|松下台灯pro+|17335|
|pmfbj.light.lz8321|松下风扇灯|8038|
|pmfbj.light.tl0666|松下台灯|10211|
|pmfbj.light.ts2001|松下落地灯|9754|
|pmfbj.light.tz8001|松下立式护眼灯|23149|
|pmfbj.light.wy0b01|松下台灯pro|11848|
|pmfbj.light.xs2403|松下智能吸顶灯Max|26453|
|pmfbj.light.xsx330|松下明畔吸顶灯|4536|
|pmfbj.light.xsx332|松下松恬吸顶灯|4976|
|pmfbj.light.xsx340|松下智能吸顶灯|7082|
|pmfbj.light.xsx341|松下吸顶灯|6857|
|pmfbj.light.xsx344|松下花吊灯|7525|
|pmfbj.light.xsx345|松下智能花吊灯|7350|
|pmfbj.light.xsx505|松下颖伦吸顶灯|4977|
|pmfbj.light.xsx880|松下智能吸顶灯pro|21055|
|ptx.light.aklig|平头熊智能射灯|30836|
|ptx.light.akligs|平头熊人体存在筒射灯|30782|
|ptx.light.aktlig|平头熊智能筒灯|33316|
|ptx.light.dd23|平头熊二三线调光灯带|31460|
|ptx.light.f5lig|平头熊F5金星调光筒射灯|30633|
|ptx.light.fargb|平头熊F1溢彩灯带(Mesh2.0)|31663|
|ptx.light.icrgbm|平头熊臻彩律动灯带|33237|
|punter.light.wy0a01|旁特照明智能筒射灯PT|32564|
|punter.light.wy0a02|旁特照明智能灯带|36233|
|pwzn.light.apple|灯带控制器|68922|
|pze.light.wy0a01|普卓尔智能灯|1944|
|qhzm.light.wy0a01|轻禾智能灯|3807|
|qimi.light.wy0a01|邮科通信智能调光灯|19732|
|qipai.light.wy0a01|企派智能筒射灯|32058|
|qipai.light.wy0a02|企派智能磁吸灯|37605|
|qiyl.light.qytsd|卡瑟维智能筒射灯 Ultra|39563|
|qiyl.light.wy0a01|企逸智能磁吸灯 Ultra|26988|
|qiyl.light.wy0a02|企逸智能筒射灯 Ultra|27153|
|qjiang.light.12mesh|GS智能Mesh色温灯Pro|21765|
|qjiang.light.mesh|QM智能Mesh色温灯|15910|
|qjiang.light.wb6sv1|QM智能WiFi色温灯|18575|
|qnzm01.light.wy0a01|QINENG智能筒射灯|38083|
|qnzm01.light.wy0a03|QINENG智能磁吸灯|40587|
|qszj.light.qszjs1|QISUMZJ超宽色域智能筒射灯|40551|
|qszj.light.wy0a01|QISUMZJ智能筒射灯|32222|
|qszj.light.wy0a03|QISUMZJ智能磁吸灯|34619|
|qszj.light.wy0a04|QISUMZJ智能筒射灯V2|34620|
|qtzm.light.qtcxd|秋田智能磁吸灯|35264|
|qtzm.light.qtdd|秋田智能灯带|35265|
|qtzm.light.qttsd|秋田智能筒射灯|35237|
|qtzn.light.httsd|禾透智能情景Mesh筒射灯|40697|
|qyds.light.wy0a01|谦中益智能灯|2283|
|qzgd.light.wy0a01|擎洲光电智能灯具|17419|
|qzy.light.wy0a01|谦中益Mesh1.0护眼灯|26003|
|qzy.light.wy0a02|谦中益Mesh2.0护眼灯|26012|
|qzy.light.wy0a03|谦中益WIFI护眼灯|26026|
|radlit.light.w00a01|RADLIT锐点智能单色灯带|29116|
|radlit.light.wy0a01|RADLIT锐点智能双色灯控制器|29115|
|radlit.light.wy0a02|锐点RADLIT磁吸灯|31181|
|radlit.light.wy0a03|锐点RADLIT筒射灯|31182|
|radlit.light.wyra01|RADLIT锐点智能五色灯控制器|29117|
|raile.light.zhzm1|智慧照明|6504|
|rayai.light.rxcxd1|日信智能磁吸灯（Mesh2.0）|38336|
|rayai.light.rxtsd1|日信智能筒射灯（Mesh2.0）|38335|
|rbe.light.wy0a01|瑞柏尔智享客厅灯|2077|
|rbe.light.wy0b01|瑞柏尔智能灯|2281|
|rinmin.light.lm01|菱敏智能筒射灯|26210|
|rinmin.light.lmddm|菱敏智能节律灯|30410|
|rjxn20.light.gxzm01|感谢智能双色温灯|10999|
|rjxn20.light.rjcxdm|RJ智能磁吸灯（Mesh2.0）|29228|
|rjxn20.light.rjddm|RJ智能灯带（Mesh2.0）|29229|
|rjxn20.light.rjdhts|RJ智能筒射灯|12362|
|rjxn20.light.rjss01|Ai双色温灯|5787|
|rjxn20.light.rjtsd1|RJ智能筒射灯 Mesh2.0|38193|
|rjxn20.light.rjxncx|RJ智能磁吸灯|12357|
|rjxn20.light.rjxndd|RJ智能灯带|12388|
|rjxn20.light.sw01|松伟智能吊灯|9480|
|rjxn20.light.ywygzn|鹦鹉易管智能调光灯|12534|
|rnlo01.light.wy0a01|瑞奈智能 筒射灯2.0|32711|
|rsdz.light.rosm11|RS智能节律双色灯带2.0|32812|
|rsdz.light.wy0a01|HR智能双色灯带|38794|
|rtzn.light.wy0a01|睿态智能筒射灯（Mesh2.0）|25996|
|rtzn.light.wy0a02|睿态智能磁吸灯(Mesh2.0)|30784|
|rtzn.light.wy0a03|睿态智能灯带(Mesh2.0)|30914|
|runmin.light.wy0a01|RUNMIN 智能灯带控制器Mesh 2.0|30359|
|runmin.light.wy0a02|RUNMIN 智能筒射灯Mesh 2.0|31746|
|rusee.light.wy0a01|如见mesh智能筒射灯M|33413|
|rusee.light.wy0a02|如见mesh智能磁吸灯M|33414|
|rutang.light.wy0a01|如糖全光谱色温灯Mesh|17562|
|rxhjgn.light.rxyhdw|罗利亚智能油画灯|37398|
|sansi.light.w00a01|三思智能爱漾台灯|25095|
|sansi.light.wy0a01|三思智能全光谱吸顶灯|25057|
|sansi.light.wy0a02|三思智能护眼吸顶灯|25058|
|sansi.light.wy0a03|三思智能夹子植物灯|25066|
|sansi.light.wy0a04|三思智能全彩筒灯|25067|
|sansi.light.wy0a05|三思智能球泡灯|25068|
|sansi.light.wy0a06|三思智毅台灯Pro|25096|
|sansi.light.wy0a07|三思高亮智能卧室吸顶灯|29293|
|sansi.light.wy0a08|三思超高亮智能客厅吸顶灯|30984|
|sansi.light.wyra01|三思智能全彩筒射灯|35112|
|sayso.light.wy0a01|SAYSO智能射灯|14885|
|scc.light.w00a1|西蒙智能轨道灯LT20|17870|
|scc.light.wy0a01|西蒙智能筒射灯|17589|
|scc.light.wy0a02|西蒙悦系列客厅灯|17833|
|scc.light.wy0a03|西蒙智能灯带控制器|17863|
|scc.light.wy0a04|西蒙悦系列吸顶灯|17879|
|scc.light.wy0a05|西蒙悦系列卧室灯|17880|
|scc.light.wy0a06|Simon智能灯带|26700|
|scc.light.wy0a07|Simon智能筒射灯|30367|
|scc.light.wy0a08|Simon智能磁吸灯|36564|
|scds.light.wy0a01|灯部尚书江山如画台灯|2943|
|scds.light.wy0a03|灯部尚书智能灯|14011|
|scisto.light.wyra01|科思顿智能灯带|31414|
|seity.light.wy0a02|西铁智能筒射灯ultra|24381|
|seity.light.wy0a03|西铁照明磁吸灯 pro|26838|
|seity.light.wy0a05|西铁照明智能灯带|36821|
|senc.light.scim20|森磁智能磁吸轨道灯|34547|
|seomsh.light.fsdmst|星月影风扇灯Master|36582|
|seomsh.light.syytdd|星月影智能一体灯带|39440|
|seomsh.light.wy0a01|星月影智能筒射灯|22809|
|seomsh.light.wy0a02|星月影智能灯带|22819|
|seomsh.light.wy0a03|星月影智能磁吸灯|22856|
|seomsh.light.wyfa01|星月影智能风扇灯|27919|
|seomsh.light.xyycx1|星月影智能磁吸轨道灯|33200|
|seomsh.light.xyydd1|星月影智能调光灯带|33199|
|seomsh.light.xyyfsd|星月影风扇灯Elite|34302|
|seomsh.light.xyysd1|星月影智能射灯|33201|
|seomsh.light.xyytd1|星月影智能筒灯|33198|
|sfl.light.aaas|FSL佛山照明云控智能灯具|3784|
|sfl.light.dl002|FSL筒灯系列|12831|
|sfl.light.dl004|FSL-晨曦护眼灯|14045|
|sfl.light.fsl001|FSL品涵系列|5505|
|sfl.light.fsl002|FSL格致系列|5507|
|sfl.light.fsl003|FSL智能照明灯系列|9009|
|sfl.light.fslbv2|FSL智能北欧吸顶灯|29672|
|sfl.light.fslcxd|FSL智曜系列磁吸灯|31972|
|sfl.light.fslv22|FSL智能北欧客厅灯|33132|
|sfl.light.lp001|FSL美家系列球泡|15361|
|sfl.light.lp002|FSL美家系列高压灯带|15372|
|sfl.light.lp003|FSL佛山照明智能吸顶灯|17401|
|sfl.light.wy0a03|FSL智能落地护眼灯|36820|
|sfl.light.wyfa01|FSL智能风扇灯|29507|
|sfl.light.wyfa02|FSL智能隐形扇叶风扇灯|35756|
|sfy.light.c001|索菲亚智能双色温吸顶灯M1|23193|
|sfy.light.cw001|索菲亚智能灯带控制盒M1|23457|
|sfy.light.dw001|索菲亚智能天境灯M1|34099|
|sfy.light.f001|索菲亚智能风扇灯M1|37558|
|sfy.light.rgb001|索菲亚智能RGB灯控制器M1|23515|
|sfy.light.s001|索菲亚智能色温灯M1|23254|
|shanh.light.wy0a01|山和照明情景智能筒射灯SH-ZN12W|37607|
|shhf.light.mhcw01|智美智能吸顶灯|5478|
|shhf.light.sfla10|变频智能风扇灯|10568|
|shhf.light.sfla12|智能变频调光风扇灯|11305|
|shhf.light.sflt11|智能调光风扇灯蓝牙版|15474|
|shhf.light.slcwb3|智能色温灯蓝牙版|11971|
|shhf.light.slcwb8|智能色温灯蓝牙版V2|14136|
|shhf.light.slwfc3|智能色温灯WiFi版|10636|
|shibei.light.wy0a01|视贝智能客厅吸顶灯|4664|
|shibei.light.wy0a02|视贝智能卧室吸顶灯|4694|
|shibei.light.wy0a03|视贝智家吸顶灯2.0|35500|
|shibei.light.wy0a04|视贝智家筒射灯2.0|35501|
|shihao.light.wy0a03|侨升护眼筒射灯S2|40929|
|shuse.light.lgt02|树色小夜灯（Mesh2.0）|32621|
|siemen.light.21nc44|西门子臻影40W卧室吸顶灯|29690|
|siemen.light.phonix|西门子弦影50W卧室吸顶灯|29046|
|signfy.light.bc0lb1|飞利浦映透智能灯|34218|
|signfy.light.bc0lt1|飞利浦PureSight Pro 灯具|35031|
|signfy.light.cc0hy6|飞利浦智能吸顶灯200W|34168|
|signfy.light.cc0lu0|飞利浦漫反射智能吸顶灯130W / 皓柔|34072|
|signfy.light.cc0sj1|飞利浦智能吸顶灯48W|33981|
|signfy.light.cc0sj2|飞利浦智能吸顶灯60W|34014|
|signfy.light.cc0sj5|飞利浦智能吸顶灯160W|34015|
|signfy.light.cc0xy5|飞利浦一体式智能吸顶灯160W|34162|
|signfy.light.cc1sy2|飞利浦智能吸顶灯48W|39686|
|signfy.light.ce13my|飞利浦星河吸顶灯 140W|31668|
|signfy.light.ce13yx|飞利浦V5吸顶灯 140W|31674|
|signfy.light.ce14v7|飞利浦V7吸顶灯 140W|32957|
|signfy.light.ce14yl|飞利浦悦璃长方吸顶灯 140W|32418|
|signfy.light.ce15v9|飞利浦V9 Pro智能吸顶灯 150W|33624|
|signfy.light.ce16mj|飞利浦明简吸顶灯 160W|30725|
|signfy.light.ce16xb|飞利浦小白吸顶灯 160W|30721|
|signfy.light.ce16yf|飞利浦逸风吸顶灯 160W|30723|
|signfy.light.ce16yh|飞利浦银晖吸顶灯 160W|30727|
|signfy.light.ce45v9|飞利浦V9 Pro智能吸顶灯 45W|33630|
|signfy.light.ce48mg|飞利浦明简吸顶灯 48W|30733|
|signfy.light.ce48my|飞利浦星河吸顶灯 50W|31671|
|signfy.light.ce48xb|飞利浦小白吸顶灯 48W|30705|
|signfy.light.ce48yf|飞利浦逸风吸顶灯 48W|30722|
|signfy.light.ce48yh|飞利浦银晖吸顶灯 48W|30726|
|signfy.light.ce48yx|飞利浦V5吸顶灯 50W|31673|
|signfy.light.ce4fyl|飞利浦悦璃正方吸顶灯 48W|32477|
|signfy.light.ce4yyl|飞利浦悦璃圆形吸顶灯 48W|32478|
|signfy.light.ce50v7|飞利浦V7吸顶灯 50W|32959|
|signfy.light.ce60my|飞利浦星河吸顶灯 65W|31670|
|signfy.light.ce60v9|飞利浦V9 Pro智能吸顶灯 60W|33629|
|signfy.light.ce60xb|飞利浦小白吸顶灯 60W|30720|
|signfy.light.ce60yx|飞利浦V5吸顶灯 65W|31672|
|signfy.light.ce60zw|飞利浦知白吸顶灯 60W|30734|
|signfy.light.ce80v7|飞利浦V7吸顶灯 80W|32958|
|signfy.light.ce85v9|飞利浦V9 Pro智能吸顶灯 85W|33625|
|signfy.light.dm0ys1|飞利浦智能射灯_Mify650|34400|
|signfy.light.dm0ys2|飞利浦智能射灯_Mify670|34401|
|signfy.light.dm0ys3|飞利浦智能格栅射灯_Mify630|34402|
|signfy.light.dm0yz1|飞利浦智能筒射灯_Mify620|34350|
|signfy.light.dm0yz3|飞利浦智能筒射灯_Mify625|34396|
|signfy.light.dm0yz5|飞利浦智能射灯_Mify630|34399|
|signfy.light.sm0yz1|飞利浦智能灯带_Mify SD200W TW|34642|
|signfy.light.sm0yz2|飞利浦智能灯带_Mify SD100W TW|34643|
|signfy.light.sm0yz4|飞利浦智能灯带_Mify SD60W TW|40270|
|ske.light.skcxd|视客智能磁吸灯|35473|
|ske.light.wy0a01|SKEN智能筒射灯|35407|
|ske.light.wy0a02|SKEN智能灯带|35409|
|skyiot.light.wy0a01|Skyiot智能筒射灯|28896|
|skyiot.light.wy0a02|Skyiot智能灯带|28897|
|skyiot.light.wy0a03|Skyiot智能磁吸灯|33821|
|skyiot.light.wyra01|Skyiot智能彩色灯带|33926|
|skzm.light.adltsd|SEECANN智能筒射灯|38407|
|skzm.light.dcdcdd|SEECANN淡彩光餐吊灯|37159|
|skzm.light.dcgdd2|SEECANN淡彩光灯带|37148|
|skzm.light.sc560z|SEECANN天际吸顶灯|33874|
|skzm.light.sktjd1|SEECANN圆形ADL天际灯|31192|
|skzm.light.sktjd3|SEECANN方形ADL天际灯|31329|
|skzm.light.wfv20|SEECANN全光谱护眼吸顶灯|39708|
|slf.light.lts01|智拉斐LED智能调光灯带TG-HY1|33003|
|slf.light.tdgd1|智拉斐嵌入式筒灯TD-GD1-75-12|38524|
|slf.light.tdkt1|智拉斐嵌入式射灯TD-KT1-75-12|38522|
|slf.light.tdkt2|智拉斐嵌入式射灯TD-KT2-75-12|38523|
|slf.light.w00a01|智拉斐Y8大板旋钮单调光|9149|
|slf.light.wy0a01|智拉斐Y8大板旋钮色温调光|9150|
|sln88.light.wy0a02|施耐朗吸顶灯|36341|
|sln88.light.wy0a03|施耐朗智能客厅吸顶灯|38313|
|smartj.light.sjdlds|SmartJoy智臻调光筒灯（蓝牙Mesh版）|3766|
|smartj.light.sjpdls|SmartJoy极智智能灯带控制器（蓝牙Mesh版）|18774|
|smartj.light.sjpdsl|SmartJoy极智调光筒射灯（蓝牙Mesh版）|18202|
|smartj.light.sjpmdc|SmartJoy极智磁吸餐吊灯（蓝牙Mesh版）|18624|
|smartj.light.sjpmdf|SmartJoy极智磁吸泛光灯（蓝牙Mesh版）|18622|
|smartj.light.sjpmdg|SmartJoy极智磁吸格栅灯（蓝牙Mesh版）|18621|
|smartj.light.sjpmds|SmartJoy极智磁吸射灯（蓝牙Mesh版）|18623|
|smartj.light.sjsdcb|SmartJoy智臻色温灯（蓝牙Mesh版）|4763|
|smartj.light.sjsdls|SmartJoy智臻调光灯带（蓝牙Mesh版）|4957|
|smartj.light.sjsdmb|SmartJoy智臻炫彩灯（蓝牙Mesh版）|4764|
|smartj.light.sjsdsl|SmartJoy智臻调光射灯（蓝牙Mesh版）|4759|
|smartj.light.sjsmdf|SmartJoy智臻磁吸泛光灯（蓝牙Mesh版）|4760|
|smartj.light.sjsmdg|SmartJoy智臻磁吸格栅灯（蓝牙Mesh版）|4761|
|smartj.light.sjsmds|SmartJoy智臻磁吸射灯（蓝牙Mesh版）|4762|
|soron.light.w00a01|知简智能单色射灯|34763|
|soron.light.wy0a01|知简智能射灯|28451|
|sover.light.wy0a01|松伟高端智能光学照明灯 QR-1|21951|
|sover.light.wy0a02|松伟高端智能装饰灯D1|22023|
|sover.light.wy0a03|松伟高端智能装饰吸顶灯XD1|22038|
|sp168.light.wy0a01|吉兆致智能灯泡Mesh2.0|36591|
|speng.light.sfddm1|松芃智能灯带|33250|
|sperll.light.cct|BanlanX色温灯|14703|
|sperll.light.cct2|BanlanX色温灯带控制器|28236|
|sperll.light.light1|BanlanX幻彩灯|11887|
|sperll.light.rgb|BanlanX彩光灯带控制器|25670|
|sperll.light.rgbcw|BanlanX彩光色温灯带|28237|
|sperll.light.sglw|BanlanX单色灯|14705|
|sperll.light.sglw2|BanlanX单色灯带控制器|28235|
|ssdg.light.ssdd01|SIASE深思智能低压灯带|38296|
|ssdg.light.sstsd1|SIASE深思智能深防眩筒射灯|38295|
|ssdg.light.ssxddw|SIASE深思智能吸顶灯（WiFi）|36595|
|ssdg.light.wy0a01|SIASE深思智能筒射灯|31395|
|ssl.light.sslrcd|SASELAN人存灯带（Mesh2.0）|38592|
|sswy.light.bjtsd|千爵智能筒射灯|38954|
|ssznkj.light.wy0a01|松鼠智能灯带|30439|
|ssznkj.light.wy0a02|松鼠情景智能磁吸灯|30512|
|ssznkj.light.wy0a03|松鼠智能筒射灯|31854|
|star1.light.wy3a02|星发现情景智能射灯|30887|
|stds.light.wyst01|胜腾灯饰吸顶灯|1833|
|stds.light.wyst02|胜腾吸顶灯|1834|
|stzm.light.wy0a01|仕先mesh智能情景灯带|26716|
|stznkj.light.wy0a01|光普顿智能筒射灯|36683|
|sy0821.light.wy0a01|viyan智能筒射灯|34952|
|sy0821.light.wy0a02|viyan智能灯带|34953|
|symi.light.lt07|亖米智能筒射灯|25449|
|symi.light.wy0a01|亖米筒射灯mesh版|10055|
|symi.light.wy0a02|亖米磁吸灯mesh版|10056|
|symi.light.wy0a03|晓翼智能灯mesh版|16688|
|symi.light.wy0a04|亖米智能灯带mesh版|17519|
|symi.light.wy0a05|亖米Mesh筒射灯Ultra|23290|
|symi.light.wy0a06|亖米Mesh磁吸灯Ultra|23315|
|symi.light.wy0a07|晓翼Mesh筒射灯Ultra|23316|
|szjzj.light.ah33c|孩视宝儿童房吸顶灯(单色)|34469|
|szjzj.light.ah33e|孩视宝儿童房吸顶灯(多色)|34471|
|szjzj.light.ah33g|孩视宝超薄半漫射儿童房吸顶灯(AH33A-G-i)|38311|
|szjzj.light.ah33i|孩视宝超薄半漫射儿童房吸顶灯(AH33-i)|39471|
|szjzj.light.hsb01|孩视宝舒目无叶风扇灯|36203|
|szjzj.light.hsbdkt|孩视宝舒目氛围客厅吸顶灯|34587|
|szjzj.light.hsbdws|孩视宝舒目氛围卧室吸顶灯|34588|
|szjzj.light.hsbktd|孩视宝舒目极简客厅吸顶灯|34585|
|szjzj.light.hsbwsd|孩视宝舒目极简卧室吸顶灯|34586|
|szjzj.light.wy0a01|孩视宝舒目筒射灯|35363|
|szlhco.light.tgd1|童视界智能落地灯|31505|
|szy1.light.wy0a01|明觅智能筒射灯|31938|
|tcll.light.wy0a01|TCL智睿吸顶灯|3837|
|tcll.light.wy0a04|TCL LED智能吸顶灯|28851|
|tcll.light.xl6601|TCL银河智能客厅灯|3998|
|tcll.light.xl6602|TCL现代家居吸顶灯|4030|
|tenle.light.wya01|TENLE智能照明|15917|
|tens.light.wy0a01|TNW自然界自然光筒射灯|31737|
|tew.light.wy0a01|泰沃智能筒射灯|31408|
|tewte.light.wy0a01|COTi 智能筒射灯2.0|31569|
|tewte.light.xtdcd2|COTi 全色域筒射灯2.0F|36981|
|tewte.light.xxtm20|COTi 智能筒射灯2.0F|34868|
|tho.light.thksdd|THO特好宽色域灯带（mesh2.0）|39383|
|tho.light.wy0a01|THO特好智能筒射灯|24926|
|tho.light.wy0a02|THO特好智能灯带|28011|
|tho.light.wy0a03|THO特好智能磁吸灯|30058|
|thzm.light.wy0a01|卓闻智能筒射灯（Mesh版）|31568|
|tofan.light.lt07|YOOMI智能双色灯D7-Mesh|20644|
|tofan.light.ltds2|悠觅智能双色灯带MESH2.0|30795|
|tofan.light.lts2|悠觅觅光智能筒射灯MESH2.0|27971|
|topwit.light.cw02|智能磁吸灯|9603|
|topwit.light.cw03|调光磁吸灯|11664|
|topwit.light.dw01|调光无主灯|11328|
|topwit.light.dwy01|智能色温灯|10673|
|topwit.light.tsl01|智能无主灯|10687|
|topwit.light.tsl02|智能线条灯|13668|
|topwit.light.tsl03|智能调光驱动|14621|
|topwit.light.tsl07|UZ智能调光驱动|19394|
|topwit.light.tsl08|UWIZE优智者智能调光筒射灯|26850|
|topwit.light.tsl09|UWIZE优智者智能调光灯带|27539|
|torbo.light.wy0a01|托博智能灯带|33123|
|tospo1.light.bpzc01|得邦照明LED 七彩球泡7W|3411|
|tospo1.light.bpzc02|得邦照明LED 七彩球泡12W|3412|
|tospo1.light.bpzp01|得邦照明A60球泡灯|3409|
|tospo1.light.bpzp02|得邦照明A70球泡灯|3410|
|tospo1.light.rpc01|得邦照明光源模组|2619|
|tqzm.light.wy0a01|企峰智能筒射灯mesh2.0|36623|
|tqzm.light.wy0a02|企峰智能灯带mesh2.0|38143|
|traxon.light.lmprgb|e:cue智能边几灯S1|30540|
|traxon.light.osltd|欧司朗桌路台灯|38589|
|traxon.light.oslxdd|欧司朗智能吸顶灯A1pro|33026|
|traxon.light.osrm20|欧司朗智能卧室吸顶灯A1pro|34520|
|traxon.light.x1|欧司朗超薄智能X1系列|18641|
|traxon.light.x2|欧司朗超薄智能X2系列|18642|
|traxon.light.x3|欧司朗智能筒射灯ODS系列|19694|
|trzn.light.msy5cd|QEEX全彩智能灯带|32992|
|trzn.light.wy0a01|QEEX智能筒射灯|23815|
|trzn.light.wy0a02|QEEX智能灯带|23820|
|trzn.light.wy0a03|QEEX智能磁吸灯|23821|
|trzn.light.wy0a04|QEEX智能灯泡|28808|
|tsd.light.amn001|通士达智慧球泡灯|4917|
|tsd.light.amn002|通士达智慧灯带|4949|
|tsd.light.h002|通士达智慧客卧灯|4066|
|tsd.light.test01|舞光I智慧 球泡灯|67742|
|tsd.light.tp1|舞光I智慧 吸顶灯|68039|
|tsd.light.tsl001|舞光I智慧 坎灯|66694|
|tsoft.light.lite1|创达小台灯|15368|
|tuodi.light.tdssd|拓迪低压智能软灯带|29203|
|tuodi.light.tdwld|拓迪低压智能氛围软灯带|29204|
|twzm.light.wy0a01|泰沃磁吸灯|2524|
|ucng.light.v8uswd|桌哒 智能LED氛围灯|27550|
|ulk.light.wy0a01|ULK-RGBCW幻彩情景LED灯带|35101|
|ulk.light.wy0a02|ULK-CW色温情景LED灯带|35132|
|unec.light.wy0a01|UNEC智能灯带|30457|
|unec.light.wy0a02|UNEC智能磁吸灯|30456|
|unec.light.wy0a04|UNEC智能筒射灯|30454|
|unec.light.wy0a05|UNEC无界筒射灯|30453|
|unec.light.wy0a06|UNEC赫拉Pro筒射灯|30452|
|unec.light.wy0a07|UNEC风驰筒射灯|30451|
|unec.light.wy0a08|UNEC风云筒射灯|30450|
|unsky.light.w00a01|天空见控轴漫反射立式护眼灯C2|28034|
|unsky.light.wy0a01|天空见漫反射节律吸顶灯XC1 Air|28785|
|uwize.light.yzl02|UWIZE优智者智能吸顶灯|33701|
|uwize.light.yzl03|UWIZE优智者智能调光灯带 Mesh2.0|34610|
|uwize.light.yzl05|UWIZE优智者智能弧面筒灯|34787|
|uwize.light.yzl06|UWIZE优智者智能射灯|35088|
|vbocga.light.wy0a01|唯宝彩佳智能筒射灯|29459|
|viewx.light.101001|inncap靓光LED灯泡（彩光版）|68251|
|viomi.light.ewf11a|云米AI智能灯带Master（双色温版）|7639|
|viomi.light.ewf11b|云米AI智能灯带Master（彩光版）|7640|
|vipl.light.v8hsm|VIPL智能筒射灯Mesh2.0|31484|
|vipl.light.v8hsm1|VIPL智能灯带Mesh2.0|31485|
|vipl.light.v8hsm2|VIPL智能磁吸灯Mesh2.0|31486|
|wainft.light.1123|馨光动感灯带(双色温)|13746|
|wainft.light.nrgb11|九轮马车RGB幻彩灯带|23829|
|wainft.light.nrgbic|馨光动感灯带控制器(RGB)|21101|
|wainft.light.rgbcwy|馨光RGBCW幻彩灯带|28002|
|wainft.light.tvsyn1|九轮马车光影同步灯带|23772|
|wainft.light.tvsyns|馨光声光影同步灯带|21046|
|wainft.light.wy0a01|馨光智能灯|2584|
|wainft.light.wy0a02|XG磁吸灯|5392|
|wainft.light.wy0a03|馨光智能灯V2|11823|
|wainft.light.wyra01|XG彩光灯带|5016|
|wanduo.light.ledw1|万多CW双色温灯带|33345|
|wbzn01.light.wzbm20|微波智能双色灯带L1|34543|
|wdc.light.wy0a01|AI美居智能灯|2900|
|wdjj66.light.zt001|维德简家橱柜灯ZT-001|24882|
|wfxx.light.12|泰孚灯控盒|18648|
|wgse.light.lcxdd|WGSE智能吸顶灯|38770|
|wgse.light.wy0a01|WGSE智能筒射灯|36297|
|wgse.light.wy0a02|WGSE智能双色灯带|38259|
|wiing.light.dmsswd|德蒙士智能节律灯|30826|
|wlg.light.rgba01|WLG淡彩系列天境吸顶灯|31368|
|wlg.light.wy0a01|WLG智能调光灯|16108|
|wlg.light.wy0a02|WLG智能磁吸灯|21671|
|wlg.light.wy0a03|WLG智能灯带|21676|
|wlg.light.wy0a04|WLG 智能磁吸灯 2.0|23656|
|wlg.light.wy0a05|WLG 智能灯带 2.0|23659|
|wlg.light.wy0a06|WLG 智能筒射灯 2.0|23661|
|wlg.light.wy0a07|WLG零频闪淡彩智能筒射灯|35231|
|wlg.light.wy0a08|WLG零频闪智能筒射灯|37142|
|wlg.light.wy0a09|WLG智能筒射灯Ultra(满血版)|38255|
|wlnkj.light.light|未来鸟灯带控制器Q2|29020|
|wpzn01.light.wptsd1|为湃健康情景筒射灯|40736|
|wyled.light.hl08|文鳐人感LED灯|27581|
|xbzhm.light.w00a01|金百丽智能单色灯|4693|
|xbzhm.light.wy0a01|金百丽智能双色灯|4681|
|xcwlj.light.xcdd1|NEONEST X1灯带(多功能)|40086|
|xdlzm.light.wy0a01|流星线智能筒射灯|29791|
|xdlzm.light.xdldd|流星线智能灯带|39362|
|xgds.light.wy0a01|诺曼尼智能灯|2055|
|xgds.light.wy0a02|诺曼尼智能吸顶灯|3214|
|xgyzm.light.lmpxgy|XGY智能节律灯带(蓝牙版)2.0|28494|
|xhl.light.wy0a01|XHL智能筒射灯L9|30831|
|xhuan.light.cxd01|苏米深度调光磁吸灯Mesh2.0|30647|
|xhuan.light.hdmi2|苏米浅彩动态灯带Mesh2.0|33279|
|xhuan.light.hdmilm|苏米浅彩影音动态灯带Mesh2.0|32715|
|xhuan.light.pbd01|苏米人存平板灯Mesh2.0|30197|
|xhuan.light.plcg06|苏米智能筒射灯(PLC版)|81007|
|xhuan.light.plcg07|苏米智能线性灯(PLC版)|81708|
|xhuan.light.plcg08|苏米智能灯(PLC版)|82195|
|xhuan.light.smdd01|苏米深度调光灯带Ultra|38029|
|xhuan.light.smfsd1|苏米空气循环扇灯Mesh2.0|37629|
|xhuan.light.smltd3|苏米人存筒灯Mesh2.0|38291|
|xhuan.light.smtsd|苏米深度调光筒射灯Mesh2.0|30810|
|xhuan.light.smtsd1|苏米人存射灯Mesh2.0|34301|
|xhuan.light.smtsd3|苏米深度调光筒射灯Ultra|38030|
|xhuan.light.splc03|苏米智能磁吸灯(PLC版)|81903|
|xhuan.light.wy0a01|苏米如影灯带|4646|
|xhuan.light.wy0a02|苏米筒灯Lite|4647|
|xhuan.light.wy0a03|苏米磁吸泛光灯|4648|
|xhuan.light.wy0a04|苏米磁吸格栅灯|4649|
|xhuan.light.wy0a05|苏米磁吸射灯|4650|
|xhuan.light.wy0a06|苏米如光筒灯|4651|
|xhuan.light.wy0a07|苏米如光射灯|4652|
|xhuan.light.wy0a08|苏米球泡灯Lite|4654|
|xhuan.light.wy0a10|苏米智能灯|5832|
|xhuan.light.wy0a11|苏米磁吸灯Pro|10362|
|xhuan.light.wy0a12|苏米线性灯Pro|10385|
|xhuan.light.wy0a13|苏米筒射灯Pro|10386|
|xhuan.light.wy0a14|苏米智能灯Pro|10387|
|xhuan.light.wy0a16|苏米节律灯|21063|
|xhuan.light.wy0a17|苏米智能灯Mesh2.0|25109|
|xhuan.light.wyrz04|苏米智能筒射灯H|15997|
|xhuan.light.wyrz05|苏米智能磁吸灯H|15998|
|xhuan.light.wyrz06|苏米智能线性灯H|15999|
|xhuan.light.wyrz09|苏米智能筒射灯Mesh2.0|27423|
|xhuan.light.wyrz11|苏米智能灯带Mesh2.0|27425|
|xhuan.light.wyrz12|苏米零频闪灯带|40367|
|xhuan.light.wyrz4s|苏米智能筒射灯Hs|21062|
|xhzm.light.wy0a01|馨宏吸顶灯|3787|
|xhzm5.light.xghm20|LEDCHB智能磁吸轨道灯|39023|
|xiaomi.light.btlm2|米家筒灯2 蓝牙Mesh版|21641|
|xiaomi.light.btlm2p|米家筒灯2 Pro 蓝牙Mesh版|21643|
|xiaomi.light.cd40|米家吸顶灯C D40|35528|
|xiaomi.light.ceil01|米家吸顶灯D20|18404|
|xiaomi.light.ceil02|米家吸顶灯D30|18405|
|xiaomi.light.ceil03|米家吸顶灯D40|18406|
|xiaomi.light.ceil04|米家吸顶灯L60|18407|
|xiaomi.light.ceil05|米家吸顶灯L90|18408|
|xiaomi.light.ceil30|米家面板灯L30 蓝牙Mesh版|19839|
|xiaomi.light.ceil60|米家面板灯L60 蓝牙Mesh版|19840|
|xiaomi.light.cfan|米家风扇灯 42英寸|16391|
|xiaomi.light.cfan01|米家风扇灯 36英寸|22378|
|xiaomi.light.cl100|米家吸顶灯C L90|35527|
|xiaomi.light.dining|米家餐厅吊灯|25565|
|xiaomi.light.dinw|米家餐厅吊灯|34828|
|xiaomi.light.r3pro|米家筒灯3 Pro 人在感应版|33934|
|xiaomi.light.s3pro|米家射灯3 Pro|32834|
|xiaomi.light.sp2|米家射灯2 蓝牙Mesh版|21642|
|xiaomi.light.sp2p|米家射灯2 Pro 蓝牙Mesh版|21644|
|xiaomi.light.t3pro|米家筒灯3 Pro|32833|
|xiaomi.light.thin|米家吸顶灯Pro 超薄 L100|28413|
|xiaomi.light.thin01|米家吸顶灯Pro 超薄 D60|28455|
|xiaomi.light.thin02|米家吸顶灯Pro 超薄 D50|28456|
|xingh.light.fsd1|风扇灯|12482|
|xingh.light.fsd2|无极调光风扇灯|12385|
|xinji.light.wy0a01|新极智能灯|16244|
|xinji.light.wy0a02|新极智能无主灯|16988|
|xinji.light.wy0a03|新极智能筒射灯Pro2.0|23217|
|xinji.light.wy0a04|新极智能灯带Pro2.0|23686|
|xinji.light.wy0a05|新极智能0眩光超凡Pro2.0|25949|
|xinji.light.wy0a08|新极智能吸顶灯Pro|35577|
|xinliy.light.wy0a01|润盛LED智能灯泡Mesh2.0|30792|
|xinliy.light.wy0a03|润盛LED智能灯带Mesh2.0|31189|
|xinliy.light.wy0a05|润盛LED一体智能灯带Mesh2.0|34055|
|xinliy.light.wyra01|润盛LED智能彩光灯带Mesh2.0|31235|
|xinuos.light.xnsttm|鑫诺仕台灯（Mesh2.0）|33224|
|xiubo.light.wy0a01|秀柏智能筒射灯|30829|
|xjzn.light.xjum20|鑫居双色温灯带 Mesh2.0|36391|
|xkai.light.wyfa01|小凯健康照明全光谱无叶风扇灯|31985|
|xkzj01.light.wy0a01|光明虎智能筒射灯|37847|
|xldzm.light.xldts1|靓度智能筒射灯Mesh2.0|38360|
|xmd.light.pbd01|星明浩人体存在平板灯|24761|
|xmd.light.wy0a06|XMH智能吸顶灯|33269|
|xmd.light.wy0a07|XMH智能LED灯带|33407|
|xmd.light.wy1a01|XMH智能筒射灯A8|30347|
|xmibox.light.1047|请勿操作本产品|80423|
|xqwgt.light.zsh|星期五潮玩展示盒|10897|
|xrx.light.xrxcgd|XRX橱衣柜智能灯带|34590|
|xry.light.wy0a01|星如雨智能灯带（双色温）|26861|
|xry.light.wy0a02|星如雨智能筒射灯|26862|
|xry.light.wy0a03|星如雨智能磁吸灯|26863|
|xry.light.wy0a04|星如雨智能吸顶灯|27037|
|xry.light.xrycxd|星如雨智能灯|12344|
|xsj.light.xsjts1|新视界智能筒射灯（Mesh2.0）|38358|
|xutian.light.wy0a01|XTIAN智能灯带|32837|
|xwiwn.light.xwl001|xiaowell小为科技智能筒射灯|35089|
|xwiwn.light.xwl002|xiaowell小为科技智能灯带|35891|
|xxczn.light.xxcts1|添宇智能筒射灯Mesh2.0|38141|
|xy001.light.sytsdm|司元智能筒射灯（Mesh2.0）|34981|
|xy8866.light.air02|XN TECH智能筒射灯Ultra|31978|
|xy8866.light.air03|XN TECH宽色域灯带Ultra|32309|
|xy8866.light.wy0a04|XN Mesh色温筒射灯|40821|
|xzx.light.wyxzx1|喜智喜智能灯|1865|
|y13t4y.light.wy0a01|费里克斯智能筒射灯|34466|
|y13t4y.light.wy0a02|翰一宸智能筒射灯|36534|
|yankon.light.cxgdd|阳光智能轨道灯|34742|
|yankon.light.wy0a01|阳光智能吸顶灯|27266|
|yankon.light.wy0a02|阳光智能吸顶灯Pro|32637|
|yankon.light.xdd01|阳光智能吸顶灯|8312|
|yankon.light.ykdd|阳光智能灯带|27254|
|yankon.light.ykmesh|阳光智能Mesh色温灯|20066|
|yankon.light.ykqpd|阳光智能灯泡|37046|
|yankon.light.yktd|阳光智能筒灯|31614|
|yankon.light.yktsd|阳光智能射灯|27255|
|ybf.light.wy0a01|一百分智能射灯|8183|
|ydsemi.light.fan01|智悦智能风扇灯|10753|
|ydx166.light.wy0a01|易得信智能筒射灯|35076|
|ydx166.light.wy0a02|易得信智能吸顶灯|35545|
|ydy.light.wy0a01|YDY情景智能筒射灯|35396|
|ydy.light.wy0a02|YDY情景智能灯带|35398|
|ydy.light.ydycxd|YDY智能磁吸灯|39273|
|yeelink.light.ble1|Yeelight 床头灯|83|
|yeelink.light.bslamp2|米家床头灯2代|882|
|yeelink.light.bslamp3|Yeelight 床头灯2代|1136|
|yeelink.light.bulb1|Yeelight 智能色温球泡|28561|
|yeelink.light.ceil26|Yeelight 纤玉吸顶灯 C2001|1815|
|yeelink.light.ceil27|Yeelight 智能客厅吸顶灯|1877|
|yeelink.light.ceil29|Yeelight 初心吸顶灯 A2001|2118|
|yeelink.light.ceil30|Yeelight LED智能吊灯|2677|
|yeelink.light.ceil31|Yeelight 智能吸顶灯 客厅款|2681|
|yeelink.light.ceil32|Yeelight LED智能吸顶灯|2892|
|yeelink.light.ceil33|Yeelight 儿童吸顶灯 C2002|3312|
|yeelink.light.ceil35|Yeelight 智能LED吊灯|4616|
|yeelink.light.ceil36|Yeelight 智能LED吊灯S|5658|
|yeelink.light.ceil38|Yeelight 智能吸顶灯|9125|
|yeelink.light.ceil39|Yeelight 智能吸顶灯升级版|17814|
|yeelink.light.ceil40|Yeelight智能LED吸顶灯升级版|19968|
|yeelink.light.ceil42|Yeelight 智能彩光吊灯|20819|
|yeelink.light.ceil45|Yeelight 超薄智能吸顶灯|21742|
|yeelink.light.ceil46|Yeelight 凌动LED吸顶灯|21743|
|yeelink.light.ceil47|Yeelight 超薄智能吸顶灯PRO|22448|
|yeelink.light.ceil55|Yeelight智能吸顶灯 氛围客厅款|26194|
|yeelink.light.ceil56|Yeelight智能吸顶灯 氛围卧室款|26196|
|yeelink.light.ceil58|Yeelight 极月吊灯 L1200|27147|
|yeelink.light.ceil59|Yeelight 吸顶灯|27844|
|yeelink.light.ceil60|Yeelight 智能色温吸顶灯|29226|
|yeelink.light.ceil63|Yeelight 智能超薄吸顶灯|34406|
|yeelink.light.ceil64|Yeelight 漫反射吸顶灯|34407|
|yeelink.light.ceil65|Yeelight 智能雷达吸顶灯 卧室款|36371|
|yeelink.light.ceil66|Yeelight 智能雷达吸顶灯 客厅款|36372|
|yeelink.light.ceil67|Yeelight超薄智能吸顶灯|39187|
|yeelink.light.ceil68|Yeelight超薄智能吸顶灯PRO|39188|
|yeelink.light.ceil69|Yeelight纤玉PLUS智能吸顶灯客厅款|39189|
|yeelink.light.ceil70|Yeelight纤玉PLUS智能吸顶灯卧室款|39190|
|yeelink.light.ceil73|Yeelight歆影PLUS智能吸顶灯卧室款|40343|
|yeelink.light.ceil74|Yeelight歆影PLUS智能吸顶灯客厅款|40347|
|yeelink.light.ceila|Yeelight 纤玉吸顶灯C2001|2782|
|yeelink.light.ceilb|Yeelight 氛围吸顶灯升级版|2972|
|yeelink.light.ceilc|Yeelight 氛围吸顶灯|3232|
|yeelink.light.ceile|Yeelight LED吸顶灯升级版|8267|
|yeelink.light.ceiling1|Yeelight LED吸顶灯|344|
|yeelink.light.ceiling10|Yeelight 皓石 LED吊灯|992|
|yeelink.light.ceiling11|Yeelight LED吸顶灯（升级版）|1141|
|yeelink.light.ceiling12|Yeelight LED吸顶灯 Pro|1140|
|yeelink.light.ceiling13|Yeelight LED吸顶灯|1139|
|yeelink.light.ceiling14|Yeelight LED吸顶灯 Mini|1138|
|yeelink.light.ceiling15|Yeelight 皎月 LED吸顶灯480（升级版）|1137|
|yeelink.light.ceiling16| Yeelight 星宇 LED吸顶灯|1206|
|yeelink.light.ceiling17|Yeelight 智能吸顶灯 卧室款|1246|
|yeelink.light.ceiling18|Yeelight LED吸顶灯 Pro|1272|
|yeelink.light.ceiling19|Yeelight RGB彩光吸顶灯 客厅款|1271|
|yeelink.light.ceiling2|Yeelight LED吸顶灯青春版|508|
|yeelink.light.ceiling20|Yeelight RGB彩光吸顶灯 卧室款|1270|
|yeelink.light.ceiling21|米家客厅吸顶灯|1296|
|yeelink.light.ceiling22|米家卧室吸顶灯450|1295|
|yeelink.light.ceiling23|米家卧室吸顶灯350|1294|
|yeelink.light.ceiling24|Yeelight 皎月 LED吸顶灯 260|1321|
|yeelink.light.ceiling3|Yeelight 皎月LED吸顶灯|513|
|yeelink.light.ceiling4|Yeelight 皎月LED吸顶灯|514|
|yeelink.light.ceiling5|米家LED吸顶灯|612|
|yeelink.light.ceiling6|Yeelight 皓石LED吸顶灯 Pro|824|
|yeelink.light.ceiling7|Yeelight 皓石LED吸顶灯|826|
|yeelink.light.ceiling8|Yeelight 皓石LED吸顶灯 Plus|825|
|yeelink.light.ceiling9|Yeelight 皓石LED吸顶灯 Pro|993|
|yeelink.light.color1|Yeelight 彩光灯泡|52|
|yeelink.light.color2|Yeelight LED灯泡（彩光版）|436|
|yeelink.light.color4|Yeelight LED灯泡1S（彩光版）|1227|
|yeelink.light.color8|Yeelight LED灯泡1S 彩光版|2061|
|yeelink.light.colora|Yeelight 彩光灯泡1SE|69201|
|yeelink.light.colorb|Yeelight LED灯泡W3（彩光版）|69739|
|yeelink.light.ct2|Yeelight LED灯泡（色温版）|526|
|yeelink.light.cta|Yeelight LED灯泡W3（色温版）|69738|
|yeelink.light.dn2grp|Mesh筒灯灯组|1047|
|yeelink.light.dnlight2|Yeelight LED筒灯|948|
|yeelink.light.fancl1|Yeelight 逸扬风扇吊灯（智能款）|1568|
|yeelink.light.fancl2|Yeelight  烁影直流变频风扇灯 S2001|1634|
|yeelink.light.fancl5|Yeelight 逸扬直流变频风扇吊灯 C900|2214|
|yeelink.light.fancl6|Yeelight 逸扬直流变频风扇吊灯 C1060|2431|
|yeelink.light.fancl8|Yeelight 智能风扇灯|21818|
|yeelink.light.lamp1|米家台灯|150|
|yeelink.light.lamp10|Yeelight 星辰落地灯|1260|
|yeelink.light.lamp15|Yeelight 显示器挂灯|70702|
|yeelink.light.lamp17|Yeelight 无线充电台灯|70706|
|yeelink.light.lamp2|米家台灯Pro|664|
|yeelink.light.lamp21|米家智能充电台灯|4737|
|yeelink.light.lamp28|米家台灯1S增强版 耀夜黑|10712|
|yeelink.light.lamp3|Yeelight 智能护眼台灯|663|
|yeelink.light.lamp30|Yeelight 立式学习灯 V8|18517|
|yeelink.light.lamp34|Yeelight 立式学习灯 V6|21727|
|yeelink.light.lamp38|Yeelight 桌面学习灯 A8 Pro|25703|
|yeelink.light.lamp39|Yeelight 显示器挂灯 Ultra|25778|
|yeelink.light.lamp4|米家台灯 1S|931|
|yeelink.light.lamp41|Yeelight 立式学习灯 V5|25790|
|yeelink.light.lamp42|Yeelight 显示器挂灯2 Pro|31535|
|yeelink.light.lamp43|Yeelight Tube Plus2屏幕挂灯|33812|
|yeelink.light.lamp5|Yeelight 智能护眼台灯 Prime|65823|
|yeelink.light.lamp7|Yeelight LED光感台灯V1|1263|
|yeelink.light.lamp9|Yeelight 星辰LED台灯|1261|
|yeelink.light.light3|米家LED筒灯 蓝牙MESH版|1772|
|yeelink.light.mb1grp|Mesh球泡灯组|1054|
|yeelink.light.mb2grp|Yeelight LED烛泡灯组|1053|
|yeelink.light.meshbulb1|Yeelight LED球泡|996|
|yeelink.light.meshbulb2|Yeelight LED烛泡|995|
|yeelink.light.ml1|Yeelight 筒射灯|2076|
|yeelink.light.ml10|Yeelight智能筒射灯|15745|
|yeelink.light.ml11|YEELIGHT凌动 智能筒射灯|17288|
|yeelink.light.ml12|YEELIGHT凌动 智能磁吸灯|17289|
|yeelink.light.ml13|Yeelight 智能筒射灯2.0|22842|
|yeelink.light.ml14|Yeelight智能磁吸灯2.0|22844|
|yeelink.light.ml18|Yeelight 智能吸顶灯mesh版 客厅款|32682|
|yeelink.light.ml2|Yeelight 色温灯泡 M2|2342|
|yeelink.light.ml20|Yeelight 智能明装筒射灯|33378|
|yeelink.light.ml23|Yeelight 智能吸顶灯mesh版 卧室款|34408|
|yeelink.light.ml24|Yeelight 智能色温筒射灯2.0|35566|
|yeelink.light.ml26|Yeelight T2智能色温筒射灯2.0|38831|
|yeelink.light.ml3|Yeelight 明装色温筒灯M1|3291|
|yeelink.light.ml6|米家智能磁吸轨道系统 格栅灯|9804|
|yeelink.light.ml7|米家智能磁吸轨道系统 线条灯|9811|
|yeelink.light.ml8|米家智能磁吸轨道系统 射灯|9812|
|yeelink.light.ml9|Yeelight智能色温筒射灯C1|11667|
|yeelink.light.mono1|Yeelight 白光灯泡|51|
|yeelink.light.mono10|Yeelight P 系列青空灯 3060|27906|
|yeelink.light.mono12|Yeelight 青空灯 G6 Pro|29342|
|yeelink.light.mono4|Yeelight LED 灯泡1S（白光版）|1242|
|yeelink.light.mono5|Yeelight LED 灯丝灯|1241|
|yeelink.light.mono7|Yeelight 青空灯|10461|
|yeelink.light.mono8|Yeelight 青空灯G6|13422|
|yeelink.light.mono9|Yeelight 青空面板灯A10|17691|
|yeelink.light.nl1|米家夜灯2 蓝牙版|2038|
|yeelink.light.nl2|米家智能光感夜灯|4736|
|yeelink.light.panel1|Yeelight 皓白 LED面板灯|862|
|yeelink.light.panel3|Yeelight 皓白 LED面板灯 Pro|1416|
|yeelink.light.panel6|Yeelight 智能面板灯|22810|
|yeelink.light.panel7|Yeelight人体存在面板灯|23762|
|yeelink.light.panel8|Yeelight M4人体存在面板灯2.0|34216|
|yeelink.light.plate2|Yeelight 智能奇光板|5134|
|yeelink.light.sp1grp|Yeelight LED射灯灯组|1055|
|yeelink.light.spot1|Yeelight LED射灯|997|
|yeelink.light.spot2|米家LED射灯 蓝牙MESH版|5741|
|yeelink.light.str1|Yeelight 智能色温灯带2.0|22843|
|yeelink.light.strip1|Yeelight彩光灯带|203|
|yeelink.light.strip2|Yeelight彩光灯带（延长版）|585|
|yeelink.light.strip4|Yeelight 泛影LED灯带|1230|
|yeelink.light.strip6|Yeelight LED 彩光灯带1S|1889|
|yeelink.light.strip8|Yeelight Chameleon 幻彩灯带|4351|
|yeelink.light.stripa|Yeelight LED 彩光灯带 1S|2889|
|yeelink.light.stripf|Yeelight C1智能高压色温灯带|11901|
|yeelink.light.stripj|YEELIGHT凌动 灯带控制器|17290|
|yeelink.light.stripk|Yeelight 智能恒压DC灯带2.0|24550|
|yeelink.light.virtual|灯组（小米 & Yeelight）|82|
|yeelink.light.vtl_ble1|Yeelight 床头灯（虚拟）|146|
|yeelink.light.wy0a01|Yeelight LED智能磁吸灯|14162|
|yeelink.light.wy0a03|Yeelight LED智能灯带|14335|
|yeelink.light.wyra01|Yeelight LED彩光灯带|14494|
|yeelink.light.yct01|Yeelight Pro 色温灯|5620|
|yeelink.light.ydim01|Yeelight Pro 亮度灯|5621|
|yeelink.light.yrgb01|Yeelight Pro 彩光灯|5539|
|yg1.light.wy0a01|情景智能灯带|29799|
|yg1.light.wy0a03|情景智能筒射灯|29801|
|yg1.light.wy0a04|情景智能吸顶灯|29802|
|yg1.light.wy0a05|情景爱眼天镜吸顶灯|32595|
|ygzm.light.wy0a01|杜蒙筒射灯X1Pro|35380|
|ygzm.light.wy0a02|杜蒙智能黑金灯带|35381|
|ygzm.light.wy0a03|杜蒙智能磁吸灯Mesh2.0|37280|
|yhj.light.wy0a01|探硕情景智能筒射灯2.0|32574|
|yhj.light.wy0a02|探硕情景智能灯带2.0|32575|
|yhled.light.yhtsm|塔普顿智能筒射灯（Mesh2.0）|37422|
|yhmesh.light.wy0a01|缘弧智能磁吸灯V2s pro|22540|
|yhmesh.light.wy0a02|缘弧智能筒射灯V2s pro|22594|
|yhmesh.light.wy0a03|缘弧智能筒射灯 V2 pro 2.0|27036|
|yhmesh.light.wy0a04|缘弧智能磁吸灯 V2 pro 2.0|27035|
|yhph.light.wy0a01|沛鸿吸顶灯|3637|
|yht.light.wy0a01|银菲特灯泡蓝牙mesh版|3753|
|yhzm.light.wyfh01|菲虹灯饰|1825|
|yilai.light.ceiling1|易来 皑月LED吸顶灯 480|977|
|yilai.light.ceiling2|易来 荷枫LED吸顶灯 430|1051|
|yilai.light.ceiling3|易来 荷枫LED吸顶灯 Pro|1052|
|yjlkj.light.wy0a01|永杰霖双色智能灯带|37051|
|yjzm.light.yjtsd1|企及照明智能筒射灯（Mesh2.0）|38381|
|yjzm01.light.wy0a01|尖硕智能筒射灯|37719|
|ykl.light.wy0a01|晶米智能筒射灯mesh版|29779|
|yky01.light.ykyts1|至御智能筒射灯 Mesh2.0 满血版|39174|
|yky01.light.zycxdm|至御智能磁吸灯（Mesh2.0）|29906|
|yky01.light.zyddm|至御智能灯带（Mesh2.0）|30133|
|yky01.light.zytsdm|至御智能筒射灯（Mesh2.0）|29592|
|yky01.light.zyxddm|至御智能护眼吸顶灯（Mesh2.0）|30342|
|ylwl.light.luwfgl|鹿家良品LED智能灯II|34265|
|ylwl.light.luwgel|鹿家良品国王湖吊灯|32548|
|ylwl.light.luwgl2|鹿家良品LED智能灯I|36126|
|ylzc.light.yldd|云犀石T0调光灯带（多功能）|40521|
|ylzm.light.wyly01|雷圆智能客厅灯|1830|
|ym001.light.v8w|炎米显示器挂灯|28325|
|ymj.light.wy0a02|EMG智能灯系列|4578|
|ymj.light.wyymj1|EMG上光环吸顶灯|1826|
|yoohoo.light.lts2|FRFOX-Z1射灯|25597|
|yoohoo.light.z2|FRFOX-Z2筒灯|37700|
|youpon.light.wy0a01|友邦智能磁吸轨道灯SD系列|30941|
|youpon.light.wy1a01|友邦智能灯带QD系列|30569|
|youpon.light.wy2a01|友邦智能筒射灯SD101-Z|30570|
|yrb999.light.wy0a01|澳浦智能筒射灯|36814|
|ys333.light.mdym20|元笙智能吸顶灯|36713|
|ysjt.light.ysxdd|YSXD智能吸顶灯（WiFi）|29352|
|ysmy1.light.wyfa01|源氏木语智能风扇灯G1|37434|
|yuerzj.light.wy0a01|鱼儿智家天空灯|14701|
|yunmi.light.ebl11b|云米AI智能灯带控制器Master S|24823|
|yunmi.light.ebl21b|云米AI智能筒射灯Master|24821|
|yunmi.light.ebl22b|云米智能射灯C1|29280|
|yunmi.light.ebl31b|云米AI智能磁吸轨道灯Master|24822|
|yuxuan.light.wy0a01|誉璇智能吸顶灯|4662|
|ywyg.light.wy1a01|黄白鹦智能筒射灯|31188|
|yyyf.light.wyfa01|永怡御风风扇灯|37303|
|yyzm.light.v8hsm|月影智能灯带（Mesh2.0）|31902|
|yyzm.light.xedts|希尔顿筒射灯（Mesh2.0）|30325|
|yyzm.light.xedxdd|希尔顿节律光2.0护眼灯air|30385|
|yyzm.light.yycx|月影智能磁吸灯（Mesh2.0）|25850|
|yyzm.light.yyhyd1|月影节律光2.0护眼灯air|29282|
|yyzm.light.yyts|月影智能筒射灯（Mesh2.0）|25280|
|yyzm.light.yyzhy1|月影节律光2.0感应护眼灯air|33549|
|yyzm.light.yyzmxd|月影节律光2.0感应护眼灯pro|27278|
|yyzn.light.wy0a01|Ai home智能灯带|14969|
|yyzn.light.wy0a02|Ai home智能磁吸灯|14970|
|yyzn.light.wy0a03|Ai home智能筒射灯|14971|
|yyzn.light.wy0a04|Ai home智能双色温灯|18183|
|zadz.light.zoa02|ZOA智能吸顶灯（Mesh2.0）|26995|
|zage.light.wy0a01|中安巨能磁吸灯Mesh2.0|29805|
|zage.light.wy0a02|中安巨能筒射灯Mesh2.0|29806|
|zage.light.wy0a03|中安巨能智能灯带Ultra2.0|33523|
|zair.light.zcw01w|ZAIR智能落地灯 增强版|9844|
|zair.light.zcw02w|ZAIR智能落地灯 常规版|10192|
|zanqi.light.v8hsm|puluoti智能筒射灯（Mesh2.0）|31919|
|zbmesh.light.wy0a01|华时智能照明|20525|
|zbmesh.light.wy0a02|ZB 智能筒射灯 MESH2.0|23517|
|zbmesh.light.wy0a03|ZB 智能灯带 MESH2.0|23528|
|zbmesh.light.zbcxdm|ZKZB智能磁吸灯Mesh2.0|36124|
|zbmesh.light.zbdcgd|ZKZB淡彩光智能灯带Mesh2.0|40882|
|zbmesh.light.zbdd01|ZKZB智能灯带Mesh2.0|39436|
|zbmesh.light.zbksdd|ZKZB超宽色域智能灯带Mesh2.0|38556|
|zbmesh.light.zbrgbm|ZKZB智能RGBCW灯带Mesh2.0|36125|
|zbmesh.light.zbtsdm|ZKZB智能筒射灯Mesh2.0|36123|
|zdzm.light.zdcxd|Thanks Lighting智能磁吸灯|38068|
|zdzm.light.zddd|Thanks Lighting智能灯带|38069|
|zdzm.light.zdtsd|Thanks Lighting智能筒射灯|38017|
|zedong.light.cdnxd1|西顿智家卧室灯|11201|
|zedong.light.cdnxd2|西顿智家卧室灯PLUS|11335|
|zedong.light.cdnxd3|西顿智家客厅灯|11304|
|zedong.light.led2|ZD蓝牙双色-筒射灯系列|19159|
|zedong.light.led3|ZD蓝牙双色-吸顶灯系列|19176|
|zhanmi.light.wy0a01|翃光智能筒射灯|37112|
|zhaoy.light.wy0a01|召阳情景智能磁吸灯|25713|
|zhaoy.light.wy0a02|召阳情景智能灯带|25714|
|zhaoy.light.wy0a03|召阳情景智能筒射灯|25715|
|zhj.light.rgbcwz|智和家动态淡彩光天幕灯|35998|
|zhj.light.wy0a01|智和家智能无主灯|18115|
|zhj.light.wy0a02|智和家智能筒射灯2.0|23839|
|zhj.light.wy0a03|智和家 智能磁吸灯2.0|25977|
|zhj.light.wy0a04|智和家 智能双色温灯带2.0|25992|
|zhj.light.wy0a05|智和家 超省电万一调光筒射灯|35522|
|zhj.light.wy0a08|智和家 智能护眼吸顶灯|39385|
|zhj.light.zhjp01|智和家PLC智能筒射灯|83383|
|zhj.light.zhjp02|智和家PLC智能线性灯|83384|
|zhunen.light.wy0a01|烛照智能灯带Ultra2.0|26644|
|zhunen.light.wy0a02|烛照智能筒射灯Ultra2.0|26652|
|zhunen.light.wy0a03|烛照智能磁吸灯Ultra2.0|26653|
|zhuow.light.wy0a01|DW情景智能灯带V2X|26917|
|zhuow.light.wy0a02|DW情景智能灯带2.0|27207|
|zhuow.light.wzzncd|DW智能双色全彩灯带（Mesh2.0）|33546|
|zichen.light.wy0a01|萧然全铜智能灯|4663|
|zksq.light.rssld|ROYAL SWAN智能沙漏灯|34866|
|zksq.light.wy0a01|ROYAL SWAN智能灯带|28254|
|zksq.light.wy0a02|ROYAL SWAN智能射灯|28255|
|zksq.light.wy0a03|ROYAL SWAN超薄智能射灯|28256|
|zksq.light.wy0a04|ROYAL SWAN智能筒灯|29460|
|zkxt.light.w00a01|中科明眸护眼吸顶灯皓月系列|18816|
|zlx.light.wy0a01|智领袖智能筒射灯御光系列|32596|
|zlx.light.zlxcxd|智领袖智能磁吸灯|33254|
|zlx.light.zlxddm|智领袖智能调光灯带|33253|
|zlx.light.zlxtsd|OZN智能筒射灯|33252|
|zlyj88.light.ypddm|雁派智能灯带（Mesh2.0）|34961|
|zlyj88.light.ypsdm|雁派智能射灯（Mesh2.0）|34955|
|zlyj88.light.yptdm|雁派智能筒灯（Mesh2.0）|34960|
|zmzm.light.wy0a01|植梦筒射灯|30134|
|zmzm.light.wy0a02|植梦全光谱灯带|31607|
|znsn.light.lts2|Thoughthome智能LED灯带|25598|
|znsn.light.ltsds2|Thoughthome 星耀款智能筒射灯|34528|
|znsn.light.v5ssw|ThoughtHome智能灯S1|13603|
|znsn.light.xiliec|Thoughthome 星芒款智能筒射灯|38005|
|znsn.light.zslgtb|Thoughthome 星辉款智能筒射灯|38004|
|znsn.light.zslt07|ZNSN智能双色灯P7-Mesh版|21611|
|zsjc.light.wy0b01|即乘智能灯|12462|
|zsjc.light.wy0b02|即乘COB筒射灯 蓝牙MESH版|12855|
|zsjc.light.wy0b03|即乘磁吸灯系列|12944|
|zsszzd.light.wy0a01|众泽智能灯带Mesh2.0|36301|
|zszm.light.wy0a02|植树照明智能射灯|1897|
|zszm.light.wy0a03|植树照明智能吸顶灯|1898|
|zszszn.light.wy0a01|ZSiNTT智能双色温筒射灯|26478|
|zszszn.light.wy0a04|ZS氛围智能灯带 2.0|38399|
|zuka.light.wy0a02|佐卡智能 筒射灯2.0|25936|
|zuka.light.wy0a03|佐卡智能 磁吸灯2.0|25940|
|zuka.light.wy0a04|佐卡智能 调光灯带2.0|25941|
|zunge.light.wy0a01|尊阁皇冠智能灯|7388|
|zxgs.light.bdcl01|蓝牙双色情景灯|10789|
|zxgs.light.mbcl01|智祥调光灯mbcl01|15141|
|zxgs.light.mdcl01|Mesh双色情景灯|8530|
|zxgs.light.wdcl01|WiFi双色情景灯|8538|
|zxzm.light.j01|京东京造吸顶灯|8579|
|zy1.light.wy0a01|ZOEE智能灯带|34467|
|zzslc.light.sll01|松联诚智能灯带|31078|
|zzslc.light.sll02|松联诚双色温筒灯S7|31080|

### 环境电器

|model|name|pd_id|
|---|---|---:|
|090615.airc.a07s|平头熊空调小精灵(Mesh2.0)|26068|
|090615.airc.fsair|平头熊F系列空调三合一旋钮面板(Mesh2.0)|28440|
|090615.airc.hyshn1|皓逸Smart Home空调旋钮面板|26280|
|090615.airc.k20|OF VRF空调内机|24504|
|090615.airc.x1air|平头熊空调三合一旋钮面板|23741|
|090615.aircondition.ktf|智能空调(VRF)|75704|
|090615.aircondition.ktp|VRF空调内机|16410|
|090615.aircondition.lkt|中央空调线控网关(MESH)|13532|
|090615.aircondition.lnk|中央空调线控网关 (PTXZN)|4359|
|090615.aircondition.x6c|X6 空调面板(PTX)|13445|
|1245.airfresh.cj300|土豆新风机FLIP|20210|
|1245.airfresh.dx400|土豆新风机SKY400|20211|
|1245.airfresh.mini2|土豆MINI|70017|
|1245.airfresh.mini6|土豆新风机MINI9|25272|
|1245.airfresh.pro9|土豆新风机PRO9|19787|
|1245.airfresh.super2|土豆 PRO|8224|
|1245.airfresh.super3|土豆 MINI5|10746|
|1245.airpurifier.dl01|土豆SUPER|66667|
|720.airp.001|xCreas智能空气净化器B300i|28051|
|759413.aircondition.iez|日立中央空调|70688|
|aden.airc.12k|VINO 轻音 变频空调 (1.5匹 一级能效)|22442|
|aden.airc.a6|VINO变频空调3匹(新二级能效)|2953|
|aden.airc.vn1p5|VINO 变频空调 (1.5匹 三级能效)|27599|
|aden.aircondition.a1|VINO变频空调（三级能效）|741|
|aden.aircondition.a2|VINO变频空调（一级能效）|842|
|aden.aircondition.a4|VINO变频空调2匹2级能效|1528|
|aden.aircondition.a7|VINO变频空调2匹(新二级能效)|3793|
|aden.aircondition.ad2p1|变频风管机|13677|
|aden.aircondition.vf1p5|VINO变频空调1.5匹（一级能效）|15588|
|aden.aircondition.xfkt1|VINO新风变频空调（一级能效）|10086|
|aden.derh.derh16|VINO 智能除湿机 16L|16821|
|aden.derh.derh20|VINO 智能除湿机 20L|26823|
|aden.derh.derh40|VINO 智能除湿机 40L|25967|
|aden.derh.derh60|VINO 智能变频除湿机 62L|33800|
|aden.derh.fight|VINO 智能除湿机 16L Pro|17678|
|aden.derh.nv40v2|VINO 智能变频除湿机|31999|
|aden.derh.tou16|VINO 智能除湿机 16L|36075|
|aden.derh.vsd30|VINO智能除湿机 30L|12107|
|aden.derh.vsid30|VINO智能变频除湿机 30L|12539|
|adream.diffuser.v1|nimin智能感应香薰机 i8 Pro|35408|
|afd.airrtc.a001|艾芬达毛巾架温控器|35159|
|air.fan.ca23ad9|艾美特空气循环扇|66514|
|air.heater.wda14|艾美特移动式地暖|67901|
|airdog.airp.p50|贝昂空气净化器|35559|
|airdog.airp.x1|贝昂空气净化器X1|20597|
|airdog.airp.x5sm|贝昂空气净化器X5S|15871|
|airdog.airp.x7pm|贝昂空气净化器X7PM|27233|
|airdog.airp.x7ppro|贝昂空气净化器X7PM Pro|38304|
|airdog.airpurifier.mn|贝昂A5/MINI空气净化器|68395|
|airdog.airpurifier.x5|贝昂X3(M)空气净化器|66196|
|airdog.airpurifier.x7|贝昂X7(M)空气净化器|66334|
|airdog.airpurifier.x7sm|贝昂X7S(M)空气净化器|66559|
|airdog.heater.n900pr|贝昂暖风机|33047|
|aisair.airfresh.asae1|艾森艾尔新风机|29148|
|aizbot.watermon.wd2|Aiasst水温度传感器M2（Mesh2.0）|40359|
|aizbot.watermon.wdj1|Aiasst水温度传感器A1（WiFi）|39782|
|aizyy.airc.air01|众益洋中央空调控制器mesh2.0 UItra版|28926|
|akt.derh.2008|FLE-2008EW|9163|
|als1.diffuser.p37hx|皓轩智能香薰机P37 Pro|36410|
|als1.diffuser.xk35|昕科智能香薰机XK35 Pro|33963|
|als1.diffuser.xk36|昕科智能香薰机XK36 Pro|33844|
|als1.fan.j15pm|科宾斯智能风扇J15-Pro max|35127|
|als1.fan.j15sl|双鹿智能风扇J15-Pro max|36581|
|als1.fan.j5kbs|科宾斯智能风扇J5 Pro Max|36933|
|als1.fan.j5sl|双鹿智能风扇J5 Pro Max|36997|
|als1.fan.j5yyz|优越者智能风扇Y5 Pro Max|36838|
|als1.fan.j90pm|科宾斯智能风扇J90-Pro max|34844|
|als1.fan.j90sl|双鹿智能风扇J90-Pro max|36110|
|als1.fan.jz5|优越者智能风扇Y90-Pro max|34616|
|als1.fan.jz8x|科宾斯智能风扇Z9-Pro max|34846|
|als1.fan.kbsz5|科宾斯智能风扇Z5-Pro max|35973|
|als1.fan.xkz5p|昕科智能风扇Z5 Pro Max|37197|
|als1.fan.y15pm|优越者智能风扇Y15-Pro max|35195|
|als1.fan.y9pm|优越者智能风扇Y9-Pro max|35446|
|als1.fan.z5sl|双鹿智能风扇Z5 Pro Max|36263|
|als1.fan.z5yyz|优越者智能风扇Z5 Pro Max|36932|
|als1.fan.z9sl|双鹿智能风扇Z9-Pro max|36157|
|als1.humidifier.js03|科宾斯智能加湿器JS03 Ultra|40261|
|als1.humidifier.js03sl|双鹿智能加湿器JS03 Ultra|40263|
|als1.humidifier.js04|科宾斯智能加湿器JS04 Ultra|40262|
|amdq.fan.amfs|爱亿馨空气循环扇|26319|
|aupu.aircondition.kc26a|奥普厨房空调KC-26/A|14135|
|aux.aircondition.hc1|奥克斯智能空调|72|
|aux.aircondition.v1|奥克斯智能空调|49|
|badian.humidifier.p1000|bures百而思纯净型加湿器|14700|
|baiten.airc.air01|贝兴中央空调控制器(MESH2.0)|23603|
|baiten.airc.air02|贝兴VRF空调|26093|
|baiten.airc.dw|贝兴通用智能空调控制器(MESH2.0)|33168|
|baomi.airpurifier.450a|豹米空气净化器2S|68874|
|bcase.heater.s2220|向物加湿取暖器-恒星|14695|
|bcase.heater.s2220n|向物加湿取暖器-恒星NEW|21712|
|bcase.heater.s2404|向物加湿取暖器-行星（Mesh）|21789|
|bcase.humidifier.s2403|向物超声波加湿器-缭绕（Mesh）|21792|
|bcase.humidifier.s2407|向物无雾加湿器-银河（Mesh）|21904|
|bcase.humidifier.s2410|向物无雾加湿器-滋润|21832|
|bds.airfresh.bdsfj|百得胜净化新风机|28815|
|bean.aircondition.tc01|智能空调助手RCS-Mesh版|16549|
|bean.airrtc.nt01|三合一温控器SR-Mesh版|17084|
|bean.airrtc.sd01|深渡智能直连温控器|21142|
|beoka.airfresh.qlm5|倍益康弥散制氧新风机QL/M5|23801|
|bj352.airmonitor.m30|352甲醛检测仪M30|1399|
|bj352.airp.y106cm|352空气净化器Y106C|4597|
|bj352.airp.y106m|352空气净化器Y106|4883|
|bj352.humidifier.h70|352 Skin加湿器|68900|
|bjakq.airfresh.zen300|空气堡智慧新风ZEN-300M|71934|
|bjdm.airfresh.test01|罗美蒂琪智能新风净化机|67236|
|bm6688.fan.002|米可白蒸发式冷风扇|25521|
|bshcn.airrtc.00iems|博世MR采暖控制器|83584|
|bshcn.airrtc.120109|博世MR采暖控制器|83655|
|bshcn.airrtc.f10720|博世MR采暖控制器|83654|
|btzn.aircondition.v1|比特空调控制器|68848|
|bull.airrtc.x01a01|公牛智能温控旋钮屏(三合一)X系列|38507|
|bwj.diffuser.bw11|SO智能香薰机S7|32832|
|bwj.diffuser.h10|SO智能香薰机S2|25493|
|bwj.diffuser.k09|SO智能香薰机S1|25297|
|bwj.diffuser.s10|SO智能香薰机S10|36692|
|bwj.diffuser.s11|SO智能香薰机S11|37302|
|bwj.diffuser.s12|SO智能香薰机S12|37777|
|bwj.diffuser.s19|SO智能香薰机S19|27558|
|bwj.diffuser.s1pro|SO智能香薰机S1Pro|25961|
|bwj.diffuser.s5|SO智能香薰机S5|26197|
|bwj.diffuser.s6|SO智能香薰机S6|26502|
|bwj.diffuser.s8|SO智能香薰机S8|34373|
|bwj.diffuser.s9|SO智能香薰机S9|35657|
|bwj.humidifier.p09|SO智能加湿器SO1|24802|
|bwk.airc.air01|泊林之风智能空调-BL1|25386|
|bymiot.airc.wlv2|未来居无线空调线控器|80636|
|bymiot.aircondition.ir2|未来居空调控制器（红外版）|70363|
|bymiot.aircondition.v1|未来居中央空调控制器|67329|
|bymiot.aircondition.wl2|未来居无线中央空调控制器|71767|
|bymiot.airp.v3|未来居智能除醛空气净化器|21163|
|bymiot.airrtc.ashp1|未来居低温空气源热泵空调温控器|37275|
|bymiot.airrtc.wkxto1|未来居新能源多功能温控器|38323|
|bymiot.airrtc.wlv2|未来居轻连温控器|17427|
|bymiot.airrtc.wlv3|未来居轻连水机温控器（Mesh 2.0）|27176|
|cetus.derh.1016|赛特斯除湿机1016|21663|
|cetus.derh.1021|赛特斯除湿机STSD20-1021/1022|13731|
|cetus.derh.wdl01|万德龙科技除湿机|22288|
|cgllc.airm.cgd1st|青萍空气检测仪 Lite|9261|
|cgllc.airm.cgdn1|青萍空气检测仪 Lite|3133|
|cgllc.airm.cgs2|青萍空气检测仪 2|3159|
|cgllc.airmonitor.s1|青萍空气检测仪|841|
|chuangmi.aircondition.a|空调|75256|
|chzyj.airc.guiji|长虹空调|83630|
|chzyj.airc.test|长虹空调|82970|
|chzyj.airc.xdl|长虹中央空调|83853|
|cnhdm.airrtc.cm1wk2|CNHDM温控器CM1（WIFI）|40006|
|cnhdm.airrtc.hdmwk|CNHDM温控器168S (MESH)|30511|
|cnhdm.airrtc.wkq01|CNHDM温控器168M（WIFI）|31616|
|cubee.airrtc.1230a|希到-空调(水)|12772|
|cubee.airrtc.1230e|希到-地暖（电）温控器|12591|
|cubee.airrtc.1230t|希到-两联供温控器|12616|
|cubee.airrtc.1230w|希到-地暖（水）|12506|
|cubee.airrtc.th123e|Heatcold地暖(电)|1622|
|cubee.airrtc.th123w|Heatcold地暖(水)|1621|
|cubee.airrtc.th125a|Heatcold空调|1612|
|cubee.airrtc.th125t|Heatcold两联供|1614|
|cuco.acpartner.ap2a|电小酷空调伴侣 AP2|20154|
|cuco.acpartner.cp6|电小酷空调伴侣CP6|75888|
|daghat.fan.v1ifm|多皓智能风扇|20610|
|daikin.airc.k32|大容量厨房(标准版/黑奢版)|79984|
|daikin.aircondition.k1|智能3D气流风管式温湿平衡型/3D气流风管式温湿平衡型|77745|
|daikin.aircondition.k10|单向气流嵌入式|77761|
|daikin.aircondition.k11|智能感知环绕气流嵌入式|77762|
|daikin.aircondition.k12|环绕气流嵌入式(全效型/低矮型)|77763|
|daikin.aircondition.k13|中静压风管机(全效型/低矮型)|77764|
|daikin.aircondition.k14|自由静压风管式|77765|
|daikin.aircondition.k15|内藏落地式(全效型/低矮型)|77766|
|daikin.aircondition.k16|明装落地式(全效型/低矮型)|77767|
|daikin.aircondition.k17|挂壁式|77768|
|daikin.aircondition.k18|智能3D气流风管式 新风净化型/3D气流风管式 新风净化型|77749|
|daikin.aircondition.k19|超薄风管式新风净化型|77750|
|daikin.aircondition.k2|超薄风管式温湿平衡型|77747|
|daikin.aircondition.k20|灯槽专用室内机标准型|77758|
|daikin.aircondition.k21|灯槽专用室内机Air Mirror黑奢型|77760|
|daikin.aircondition.k3|衣帽间防潮嵌入式标准式|77748|
|daikin.aircondition.k4|智能3D气流风管式PM2.5净化型/3D气流风管式PM2.5净化型|77751|
|daikin.aircondition.k5|超薄风管式PM2.5净化型/超薄风管式标准型|77752|
|daikin.aircondition.k6|智能3D气流风管式标准型/3D气流风管式标准型|77753|
|daikin.aircondition.k7|超薄风管式大容量型|77754|
|daikin.aircondition.k8|卫浴用嵌入式标准型|77755|
|daikin.aircondition.k9|高耐久厨房用嵌入式标准型/大容量型|77756|
|daikin.airfresh.k22|全热交|77772|
|daikin.airfresh.k30|明装新风净化系统(转角卫士)|77774|
|daikin.airfresh.k33|双直流马达新风奢悦系列/双直流马达小型新风系列|79986|
|daikin.derh.k31|无水除湿机(晴天轮)|77776|
|davell.airrtc.dv323x|采暖温控器|4124|
|deerma.humidifier.jsq1|米家智能除菌加湿器  S|68750|
|deerma.humidifier.jsq2g|米家智能除菌加湿器2|7629|
|deerma.humidifier.jsq4|米家纯净式智能加湿器|3054|
|deerma.humidifier.mjjsq|米家智能除菌加湿器|66166|
|deerma.humidifier.rz300|德尔玛热蒸馏加湿器|3418|
|demry.airc.temp|DigSmart中央空调控制器|30143|
|demry.airc.tempp|DigSmart中央空调线控器|31162|
|deye.derh.u20a3|德业除湿机DYD-U20A3|1373|
|deye.derh.w20a|德业除湿机W20A3|30382|
|deye.derh.z12a3|德业除湿机DYD-Z12A3|69405|
|deye.derh.z20|德业除湿机DYD-Z20B3|12176|
|dhdzkj.airc.air01|迪航空调智能控制网关 G/Z 770|17931|
|di8hao.heater.m3|采暖温控器DKM3|71093|
|disen.airfresh.ds300|劳力特新风机|6747|
|disen.airrtc.8908b|小松鼠温控器|7982|
|disen.airrtc.rebeng|小松鼠热泵温控器|7377|
|dlx.acpartner.deim03|德力西电气空调伴侣M03|31375|
|dmaker.fan.p23|米家直流变频两季扇|5482|
|dnake.airc.temp|狄耐克VRF中央空调控制器(Mesh2.0)|34502|
|dnk.airc.dag60a|狄耐克四季生态空调|22867|
|dpurat.airc.dbdf|德普莱太环控一体机新风除湿空调|25584|
|duka.airm.hf1|杜克HF1智能多功能甲醛监测仪|22020|
|dwjxf.airfresh.bdair|第五季新风机|14814|
|dwjxf.airfresh.bdair3|第五季新风机M|19814|
|eairpo.airp.ibta10|爱璐仕智能床头柜|10038|
|ecosnu.airfresh.eksn1|恩科思奈新风机（Mesh2.0）|29144|
|edon.humidifier.s108e1|Edon爱登39°加湿器|3860|
|era.airp.cwb03|冰箱除味杀菌器Max|4617|
|era.diffuser.ws01|智能除味器|6388|
|ermi.airp.th158|yeme空气净化器|33193|
|ermi.fan.zl2025|yeme电风扇|34220|
|etern.airfresh.nh550|心之净智慧新风机|2125|
|fawad.acpartner.3303|FOWAD企鹅小墨空调伴侣|27882|
|fawad.airc.5001|FOWAD空调VRF网关Mesh2.0|34380|
|fawad.aircondition.3010|FOWAD 空调温控器2|14652|
|fawad.aircondition.3019|FOWAD空调控制器尊享版|13572|
|fawad.airfresh.220126|FOWAD新风控制器尊享版|20868|
|fawad.airrtc.30011|FOWAD 中央空调VRF控制器|70495|
|fawad.airrtc.30012|畅享版VRF空调控制器 FOWAD|6174|
|fawad.airrtc.30015|星空版VRF空调控制器 FOWAD|10760|
|fawad.airrtc.40011|FOWAD地暖温控器|71200|
|fawad.airrtc.fwd20011|FOWAD 中央空调温控器|66579|
|fbs.airm.pth3mw|测小菲空气检测仪（甲醛）PTH-3MW|22886|
|fbs.airmonitor.pth02|测小菲甲醛监测仪|1809|
|fjsjdq.heater.23180|帝仕尼取暖器|23614|
|flashm.fan.608|喵动力手持桌面二合一风扇608|39318|
|flashm.fan.f1|喵动力桌面循环扇F-1A|28069|
|flashm.fan.fa9|喵动力壁挂循环扇FA9|38703|
|flashm.fan.s35|喵动力桌面循环扇S35|38704|
|flashm.fan.zl899|喵动力夹式桌面扇ZL899|38597|
|forblu.airp.lzp2|蓝主角智能除醛空气净化器|22016|
|fungu.fan.nkbds1|繁谷多功能吊扇|33780|
|fzypyx.derh.snyp13|苏宁宜品除湿机|18394|
|giot.airrtc.v1itcw|Gra智能温控器V1（WiFi）|19930|
|giot.heater.v13daf|厚荣捷雾化壁炉|21569|
|giot.heater.v1ihm|V1Gra智能电暖器（Mesh）|23366|
|giwu.airrtc.temp|GW三合一温控器MESH2.0|32771|
|gl2023.fan.6d|Glasslock电风扇|36030|
|gl2023.fan.v1|Glasslock直流变频落地扇|36154|
|glkj.diffuser.glxxj|GL智能香薰机|34153|
|gneair.humidifier.hum01|格恩加湿器|23232|
|gneair.humidifier.hum02|GNEAIR加湿器|35352|
|googo.airrtc.air02|mitch三合一温控器（Mesh2.0）|32823|
|googo.airrtc.air04|mitch空调温控器（Mesh2.0）|34086|
|grlin.airrtc.gl8828|GRLIN智能温控器|25196|
|grlin.airrtc.zl|GRLIN智能温控器（直流）|32387|
|gswl.diffuser.xxjx1|HD智能香薰机X1（BLE)|26230|
|gswl.fan.fsx1|HD智能壁挂风扇Z701|26469|
|gswl.fan.v1sfz1|HD智能风扇Z1（BLE）|27306|
|gswl.fan.x1sfb|HD智能风扇X1（BLE）|26080|
|gydzkj.fan.xzfsw|比赛小猪水冷塔扇（WiFi）|34281|
|gydzkj.heater.xzqnq|比赛小猪取暖器|29240|
|hanyi.airpurifier.kj550|美倾净化器MIX|67790|
|hcsp.fan.fsns1|奥克斯智能风扇NS-11|36327|
|hcsp.fan.fsns2|奥克斯智能风扇NS-12|36331|
|hcsp.fan.fsns3|奥克斯智能风扇NS-13|36332|
|hcsp.fan.fsns4|奥克斯智能风扇N182|37038|
|hcsp.fan.hsfs|SAPI智能风扇|28368|
|hdc.acpartner.ym01|希虹小火箭空调伴侣|36105|
|hdl.airrtc.hdl001|HDL小懒控 智能温控器|35606|
|helans.heater.hlsqnq|禾兰仕取暖器|30814|
|hevo.airrtc.hw75pr|北极猫智能零冷水温控器|29294|
|hguang.heater.qnq02|HPUS石墨烯取暖器|30891|
|hjhr.fan.hcz11a|皇家惠人10寸折叠伸缩扇HCZ11A|13388|
|honyar.airrtc.zpa3a1|鸿雁智能三合一温控器|28608|
|hou123.fan.sxdfs|SX-SHUNXIANG循环扇|33503|
|hss.airp.kj360|summerlook宠物空气净化器|28067|
|hvac.airrtc.11m0|默哈孚嵌墙式室内温控器|9946|
|hzyk.acpartner.kt5s01|初刻良品智能空调遥控器|28868|
|idelan.aircondition.g1|金兴智能空调|244|
|idelan.aircondition.g2|金兴智能空调|243|
|idelan.aircondition.v1|金兴智能空调|101|
|idelan.aircondition.v2|金兴智能空调|185|
|ilvsd.heater.dl|利维斯顿取暖器|6316|
|ilvsd.humidifier.jl|利维斯顿加湿器|6318|
|invtop.airp.colin|爱迪生 Colin Pro 空气净化器|30337|
|invtop.airp.mars|爱迪生 Mars 空气消毒机|29042|
|invtop.airp.miro|爱迪生 Miro Pro 空气净化器|31553|
|invtop.derh.airon|爱迪生 Arion 压缩除湿机|30338|
|iot.acpartner.x1|BUSAYTY空调伴侣(插座版本)|21057|
|iot.acpartner.x2|BUSAYTY空调伴侣(USB版本)|22550|
|iot.airm.kt1|卡诺亚空气检测仪|20814|
|iot.airp.wg03|QD空气净化加湿一体机|20015|
|iot.diffuser.h2|智能香薰机|15083|
|iot.heater.qnq01|环幕取暖器|22966|
|iracc.aircondition.d19|好享+智能空调网关|66113|
|ishima.derh.001|伊岛除湿机M30 Pro|19875|
|ishima.derh.002|伊岛除湿机EF60|21605|
|jdjz.airp.kj410|京东京造 加湿空气净化器|30259|
|jdjz.airp.kj500|京东京造 宠物空气净化器|30261|
|jdjz.airp.v1|京东京造 加湿空气净化器KJ801G|35065|
|jdjz.airp.v2|京东京造 加湿空气净化器KJ1200G|35312|
|jdjz.derh.0l20|京东京造家用除湿机OL20-BD068BF|37269|
|jdjz.fan.2072fc|京东京造空气循环扇XD-2072FC|35067|
|jdjz.fan.35e2r|京东京造电风扇(带驱蚊装置)FS-35E2RY|35697|
|jdjz.humidifier.jz18b|京东京造智能电解水无雾加湿器|29854|
|jdyg.heater.j1|焦点阳光电暖器J1|30671|
|jhkdz.humidifier.j3|品源瑞J13智能加湿器|34103|
|jiebao.heater.hgp01|惠格普石墨烯取暖器|33573|
|jinpin.derh.ct16|今品家用除湿机CT16|19923|
|jipin.fan.008|即品智能风循环落地扇|25884|
|jipin.fan.010|即品风随温变智能循环扇|27074|
|jipin.fan.011|即品节能风平面扇|27314|
|jipin.fan.012|即品水冷塔扇|29062|
|jipin.fan.6c|即品一级能效节能直流风扇|35389|
|jipin.fan.f001|即品智能落地风扇|13619|
|jipin.fan.f003|即品智能互联空气循环扇|19155|
|jipin.fan.f004|即品立式空气循环扇|19353|
|jipin.fan.f005|即品空气循环扇|20224|
|jipin.fan.f006|即品智能互联平面落地风扇|20254|
|jipin.fan.f007|即品智能壁挂循环风扇|25034|
|jipin.fan.f008|即品一级能效壁挂风扇|35883|
|jipin.heater.2081|即品室内加热器|24095|
|jipin.heater.2207|即品加湿火焰净化取暖器|17490|
|jipin.heater.22071|即品互联循环风取暖器Pro|31759|
|jipin.heater.my204|即品智能电暖器|1677|
|jipin.heater.xh7121|即品室内智能立式加热器|30405|
|jlk.fan.jlkf1|BLEMOFF智能循环扇|35019|
|jmjl.fan.jlpqs|金羚智能夜灯排气扇|29913|
|jqj.heater.dnq001|金旗舰电暖器J1|30748|
|juhl.airc.room|海信智能室温线控器|80521|
|juhl.airc.water|海信智能水温线控器|80522|
|juhl.aircondition.a11|智能空调|66503|
|juhl.aircondition.hvac|海信智能中央空调|79502|
|juhl.airfresh.cat1|海信智能新风机|80498|
|jya.heater.sha1|Jya对流电暖器|1752|
|kadeer.derh.2202|奥克斯KDY-DP22A1智能除湿机|13354|
|kadeer.derh.x1701|奥克斯KDY10-01WS智能除湿机|13416|
|kadeer.fan.30ar|至凡FS-30ARL风扇|4955|
|kadeer.fan.l15br|至凡FLS-L15BRL无叶冷风扇|4983|
|kadeer.fan.l20xh|至凡FKYT-L20XHDCL落地扇|4982|
|kadeer.fan.ts45hr|至凡FT-TS45HRLDC直流塔扇|4956|
|kadeer.heater.12b5rw|至凡室内加热器（电热油汀）|3705|
|kadeer.heater.15b6rw|至凡带壁挂电热油汀|3706|
|kadeer.heater.200krw|奥克斯塔式暖风机 A1|16189|
|kadeer.heater.20yrw|至凡室内加热器（挂壁暖风机）|3707|
|kadeer.heater.b73brg|至凡室内加热器(对流式电暖器)|3708|
|kadeer.heater.b81rw|奥克斯对流式取暖器 A1|16058|
|kadeer.heater.l200mr|至凡石墨烯踢脚线电暖器|7094|
|kadeer.heater.l220ir|至凡室内加热器(踢脚线电暖器)|3709|
|kaenou.fan.fs05|QYGQ桌面风扇B05|36200|
|keey.airrtc.qyvrf1|KEEY中央空调VRF智能温控器Mesh2.0|31478|
|kegao.diffuser.gream|浅草织梦香薰机pro|35071|
|kegao.diffuser.m1pro|浅草喷香精灵pro|23185|
|kegao.diffuser.yinyue|浅草今汐香薰机pro|34921|
|kesjar.humidifier.16pro|KESIJAR智能加湿器K16pro|33764|
|kesjar.humidifier.lyjsq|科斯佳K16智能加湿器|29548|
|kesjar.humidifier.znjsq|KESIJAR智能加湿器K50|30567|
|klwdz1.airc.001|VRF智能空调|25333|
|klwdz1.airc.003|VRF智能空调MESH版|27899|
|kmhb.fan.kmf1|卡曼智能循环电风扇|15321|
|kms.heater.kmlv1|康慕林壁炉电暖器|37818|
|kmt.airrtc.xxx002|Komacht低温空气源热泵空调温控器|32865|
|kmt.airrtc.ytl001|KOMACHT新能源多功能温控器|32857|
|kotei.airrtc.ktt001|KOTEI石墨烯温控器|20923|
|koxi68.fan.892|DS802桌面循环扇|36071|
|koxi68.fan.ds301|DS301桌面循环风扇|36865|
|koxi68.fan.ds803|DS803夹子循环风扇|37589|
|lab.airp.air01|DADDYLAB空气净化器L1|24407|
|laiex.fan.lesfs|方频智能风扇（BLE）|25463|
|lanbo1.fan.lbfs1|蓝伯摇头桌面循环扇|35805|
|lat888.airrtc.wk06|迅为智能温控器Mesh2.0|26408|
|lemesh.acpartner.zirc07|中弘空调伴侣ZIRC07|29880|
|lemesh.airc.air01|情景Mesh空调室内机控制器|19340|
|lemesh.airc.air02|中弘VRF中央空调控制器(MESH2.0版)|26668|
|lemesh.airc.air03|中弘VRF中央空调控制器PRO(MESH2.0版)|27683|
|lemesh.airc.b19d|中弘两联供空调控制器(MESH2.0版)|28491|
|lemesh.airc.b27m|中弘空调室内机控制器(MESH2.0版)|27838|
|lemesh.aircondition.a01|HT智能空调控制器（Mesh版）|15797|
|lemesh.airrtc.t16|情景Mesh温控器（三合一版）|18410|
|leshow.fan.ss310|乐秀风扇 SS310|1200|
|leshow.fan.ss320|乐秀风扇 SS320|1129|
|leshow.fan.ss4|无叶塔扇|1127|
|leshow.humidifier.is2|乐秀纯净型加湿器 IS2|67511|
|line.airc.air02|邮科通信空调伴侣K6|22947|
|line.airc.fktbl|方舟鱼空调伴侣K6|27737|
|line.airc.ktbl|LineHope空调伴侣K6|27661|
|linked.airrtc.st843|零狗智能青春版温控器ST843|31405|
|linked.airrtc.st851|零狗智能青春版温控器ST851|32585|
|linp.aircondition.vrf02|领普VRF空调|15500|
|linp.airrtc.s1tdw|领普温控器S1T|19979|
|linp.airrtc.th113|领普智能温控器TH1(两联供）|9957|
|lmdq.airp.dtha02|罗美蒂琪DTH-A02空气消毒机|74190|
|lmkj.acpartner.bf1001|BOFON智能空调遥控器|23204|
|lmkj.acpartner.wsd001|BOFON空调遥控器PRO（温湿度版）|29585|
|lonink.airc.ln051|朗宁风管机空调控制器WiFi|28788|
|lonink.airc.ln052m|朗宁风管机空调控制器Mesh2.0|28361|
|lonink.airc.ln059|朗宁VRF中央空调控制器Pro Mesh2.0|26849|
|lonink.airc.ln059a|朗宁VRF中央空调控制器ProAI Mesh2.0|37683|
|lonink.airc.ln059e|朗宁VRF中央空调控制器ProE Mesh2.0|29641|
|lonink.airfresh.ln056|朗宁新风系统控制器WiFi|35798|
|lonink.airrtc.ln060|朗宁全面屏三合一温控器Mesh2.0|36241|
|lsg.heater.zpst01|中普斯特石墨烯取暖器|33136|
|lumi.acpartner.mcn04|米家空调伴侣Pro 万能遥控版|4127|
|lumi.acpartner.v1|Aqara 空调伴侣|245|
|lumi.acpartner.v2|米家空调伴侣|394|
|lumi.acpartner.v3|Aqara 空调伴侣(升级版)|497|
|lumi.aircondition.acn05|Aqara空调伴侣 P3|69068|
|lumi.airrtc.tcpecn01|空调温控器|722|
|lumi.airrtc.tcpecn02|空调温控器 S2|836|
|lumi.airrtc.vrfegl01|VRF空调控制器|718|
|luxs.heater.lxseht|炉先生智能电暖桌|22970|
|lxzn.acpartner.lx03|XIHO空调伴侣Lite|23579|
|mantic.diffuser.hym550|花悦梦香薰机 550|31840|
|mate.airfresh.a1|MATE新风机A1|8344|
|mate.humidifier.cs01|MATE加湿器|1992|
|maxi.airc.a07s|迈斯空调小精灵Mesh2.0|26398|
|maxi.airc.air03|迈斯小精灵空调控制器|19342|
|maxi.airc.air04|迈斯VRF中央空调控制器|20483|
|maxi.airc.air08|迈斯VRF空调控制器Mesh2.0|27521|
|maxi.airc.airm1|品达小精灵空调控制器Mesh2.0|35667|
|maxi.airc.airw1|品达小精灵空调控制器WIFI版|35565|
|maxi.airc.ln069s|品达中央空调|25051|
|maxi.aircondition.air02|迈斯风管机控制器A06B|15840|
|maxi.aircondition.m07|中央空调|76504|
|maxi.airfresh.fresh2|品达小精灵新风控制器Mesh2.0|35754|
|maxi.airrtc.pdkw00|品达VRF三合一温控器Mesh2.0|36720|
|mbo.airc.mac35|meipont变频空调|17758|
|mbo.aircondition.mah35|meipont热泵空调|16804|
|mdk00.airrtc.xhxto1|麦德凯MDK智能热泵温控器|39158|
|mdl.airfresh.dyd1|迈迪龙双向流低能耗新风机D1|26841|
|mhaq.aircondition.miair|三菱重工海尔·智能空调|71403|
|miaomiaoce.airm.air01|秒秒测空气质量检测仪|69671|
|miaomiaoce.airm.air02|秒秒测空气质量检测仪（甲醛）|72988|
|miaomiaoce.airm.air03|秒秒测空气质量检测仪|81470|
|miaomiaoce.airm.co2|秒秒测二氧化碳检测仪（轻享版）|27615|
|miaomiaoce.airm.hcho3|秒秒测便携甲醛检测仪|31047|
|miaomiaoce.airm.kl01|空气质量检测仪（甲醛+温湿度）|76582|
|midea.aircondition.v1|美的空调-i青春|45|
|midea.aircondition.xa1|美的空调 - 酷金|129|
|midea.aircondition.xa2|美的空调 - 酷金|360|
|miir.aircondition.ir01|空调遥控|65724|
|miir.aircondition.ir02|空调遥控|65723|
|miir.airpurifier.ir01|空气净化器遥控|65717|
|miir.fan.ir01|风扇遥控|65721|
|miot.aircondition.cl801|cl801|74698|
|miot.aircondition.v1|智能空调|9827|
|miqu.fan.lmzm2|觅贽桌面折叠扇|36870|
|mirsz.airc.ac300s|罗威亚中央空调|28752|
|mirsz.airc.air9|罗威亚中央空调智能温控器|33437|
|mirsz.airm.et61|罗威亚智能空气环境检测仪|31699|
|mirsz.airm.et71|罗威亚AI空气环境检测仪|29023|
|morlin.fan.dsnfan|帝仕尼智能风扇(WiFi)|26981|
|morlin.fan.ymfan|圆米智能风扇（WiFi）|25409|
|mrbond.airp.h1pro|邦先生智能除味器|4598|
|muxnw.airrtc.m76|慕向暖阳加热杯垫M76|23136|
|muxnw.fan.m75|慕向引擎循环扇M75|24244|
|nbaldq.heater.t21sw1|志高室内加热器（移动式地暖）|23808|
|nbfdzn.derh.cs01|forestlife除湿机FLE20-5252|8465|
|nbrs.airp.01|除醛仪 RS-JQ001|15949|
|nbsxh.fan.alw5dw|苏宁宜品冷风无叶扇( 杀菌加湿版 )|13466|
|nbsxh.heater.t21sw|苏宁宜品室内加热器（移动式地暖）|16279|
|netiot.airrtc.net04|纽恩泰空气能温控器|28724|
|nhkj15.airrtc.hoer36|暖猴智能温控器A36|36219|
|nhkj15.airrtc.hoer90|暖猴智能温控器G90|36220|
|nhy.airrtc.v1|丹麦格澜供暖|127|
|nhy.rtc.pexrtc730|丹麦格澜空调|265|
|njjlzk.airrtc.air|智精灵三速空调温控器|31030|
|njjlzk.airrtc.air2|智精灵空调地暖二合一温控器|31423|
|njjlzk.airrtc.air3|智精灵新风温控器|32376|
|njjlzk.airrtc.air4|智精灵水地暖温控器|32836|
|njjlzk.airrtc.air5|智精灵电地暖温控器|35452|
|nuanji.airrtc.nj001|暖季温控器|81270|
|nvcsmt.acpartner.fbs102|雷士空调伴侣|29434|
|nwt.airc.ac0105|NWT 变频空调|21670|
|nwt.airc.max|NWT智能移动空调MAX|36938|
|nwt.airc.wap31a|NWT互联网移动空调Pro|18423|
|nwt.aircondition.26eaw1|NWT互联网移动空调|2389|
|nwt.aircondition.26ebw1|NWT智能移动空调|15195|
|nwt.airp.kj02|NWT智能空气净化器|34303|
|nwt.airp.kq01|NWT互联网空气净化器|19101|
|nwt.derh.16l|NWT智能除湿机16L|22345|
|nwt.derh.24wu1|NWT互联网空净除湿一体机24L|14126|
|nwt.derh.30l|NWT智能除湿机30L|26119|
|nwt.derh.312en|NWT互联网除湿机 12L|1769|
|nwt.derh.330ef|NWT 互联网除湿机 30L|1720|
|nwt.derh.35l|NWT互联网变频除湿机35L|18424|
|nwt.derh.60l|NWT互联网除湿机 60L|14324|
|nwt.derh.las20l|Lumias 20L除湿机|21467|
|nwt.derh.lua12l|Lumias 12L除湿机|21468|
|nwt.derh.lua30l|Lumias 30L除湿机|21371|
|nwt.derh.n23l|NWT智能除湿机23L|33968|
|nwt.derh.nwt10l|NWT互联网除湿机 10L|14323|
|nwt.derh.nwt12l|NWT智能除湿机12L|26120|
|nwt.derh.wdh318efw1|NWT 互联网除湿机 18L|1128|
|nwt.fan.16l|NWT互联网直流变频电风扇|15397|
|nwt.fan.xh001|NWT智能空气循环扇|26598|
|odysec.airm.oem001|ODYSEC环境监测仪|29684|
|oit.acpartner.cb1b|欧伦特空调伴侣CB11|30429|
|oksen.derh.001|欧克森除湿机|26713|
|oott.humidifier.ttd02|它它你你智能宠物护理仪|30060|
|oujing.derh.137e|欧井除湿机OJ-137E|8127|
|oujing.derh.225e|欧井除湿机OJ-225E|6291|
|ouxim.airrtc.oxmwk|OUXIM三合一智能温控器|28590|
|ows.heater.pdeh1a|Focus电暖器|67519|
|ows.heater.pdeh2a|欧伟士智能电暖器3T|67629|
|ows.heater.pdeh3a|欧伟士智能电暖器Pro|71211|
|ows.heater.pro2|欧伟士智能电暖器PRO2|6929|
|ows.heater.yudi20|欧伟士浴帝|70457|
|parkoo.derh.cf138b|百奥除湿机PD-V110|25879|
|pesgd.airp.65c6vx|松下加湿空气净化器F-65C6VX|37910|
|pesgd.airp.c5pjd|松下等离子体空气净化消毒机|31501|
|poemik.watermon.9|诗墨科技鱼缸水质检测器|36862|
|ptx.airc.f1kt1|平头熊三合一屏显空调面板（F1)|37123|
|ptx.airc.fgkt1|平头熊三合一屏显空调面板(梵高）|34430|
|pxiang.fan.2310|苏宁宜品智能循环风扇|14029|
|qdhkl.airc.19se|中弘VRF中央空调控制器MESH2.0|28690|
|qdhkl.airc.a19s|中弘VRF空调Ultra|28418|
|qdhkl.airc.a42|中弘两联供空调室内机|27675|
|qdhkl.airc.acp|中弘VRF空调|82092|
|qdhkl.airc.b19c|中弘VRF中央空调控制器PRO MESH2.0|32164|
|qdhkl.airc.b19cd|中弘两联供空调控制器PRO MESH2.0|31367|
|qdhkl.airc.b19cm|中弘VRF中央空调控制器(MESH2.0版)|35421|
|qdhkl.airc.b19m|中弘VRF中央空调控制器(MESH版)|18764|
|qdhkl.airc.b19sep|中弘VRF中央空调控制器SE PRO MESH2.0|39889|
|qdhkl.airc.b25p|中弘空调室内机控制器Ultra(Wi-Fi版)|29377|
|qdhkl.airc.b27m|中弘空调室内机控制器(MESH2.0版)|35433|
|qdhkl.airc.b27p|中弘空调室内机控制器PRO(Wi-Fi版)|36541|
|qdhkl.airc.b27se|中弘空调室内机控制器SE MESH2.0|29869|
|qdhkl.airc.ln0589|LONINK VRF空调控制器PRO（Mesh）|21543|
|qdhkl.airc.s26se|中弘智能空调旋钮温控器MESH2.0|35429|
|qdhkl.aircondition.ac|VRF空调|8494|
|qdhkl.aircondition.b23|中弘空调室内机控制器(WIFI)|8491|
|qdhkl.aircondition.b25|中弘空调室内机控制器(MESH)|9507|
|qdhkl.aircondition.b27|中弘空调室内机控制器(Wi-Fi版)|15824|
|qdhkl.aircondition.loac|朗宁VRF空调室内机|13447|
|qdhkl.aircondition.md01|苏米中央空调控制器|4229|
|qdhkl.airfresh.fb27|中弘新风通用控制器|17364|
|qdhkl.airrtc.ft18|中弘智能三合一全面屏温控器水机版|38001|
|qdhkl.airrtc.t15|中弘三合一温控器|15850|
|qdhkl.airrtc.t19|中弘智能三合一旋钮温控器MESH2.0|37662|
|qdhkl.airrtc.t19f|中弘智能三合一旋钮温控器水机版|39364|
|qdhkl.airrtc.tms01|中弘智能三合一全面屏温控器MESH2.0|34090|
|qjiang.acpartner.ac02|ICX智能空调遥控器|21899|
|qjiang.acpartner.rsh01|RSH智能空调遥控器|27610|
|qjiang.acpartner.wb20|ICX智能空调遥控器|17765|
|qjiang.fan.gs02|GS智能风扇J15 Max|26240|
|qjiang.fan.j90|GS智能风扇J90 Max|28475|
|really.heater.f1|锐力电暖气|68059|
|rfd.airfresh.rdf01|RIFINDE空气全屋定制|18516|
|riot.acpartner.xiya03|希崖空调插座XyPro|25692|
|riot.heater.002|先锋油汀取暖器L9|23871|
|rtako.heater.rtknf|RTAKO智能暖风机|29001|
|rw02.fan.rw001|RW智能直流变频风扇|35174|
|saec.airc.rac|三菱电机空调|80096|
|san.airrtc.8909h|SANCORY地暖温控器|14539|
|san.airrtc.9909a|Sancory智能温控器|20589|
|san.airrtc.9909ec|Sancory智能EC温控器|23925|
|san.airrtc.9909h|Sancory智能地暖温控器|22831|
|san.airrtc.s89h|晟科瑞地暖温控器|4670|
|scdvb.airc.ktmini|SoChuang空调控制器Mini|37089|
|scdvb.airc.llg20|SoChuang 两联供空调智能控制器|38591|
|scdvb.airc.t001|SoChuang VRF中央空调控制器 Ultra|24993|
|scdvb.aircondition.acm|蓝牙VRF中央空调控制器|14050|
|scdvb.airfresh.xf20m|SoChuang智能新风机控制器Mini|33230|
|scdvb.airfresh.xf20v2|SoChuang智能新风机控制器Ultra|30299|
|scdvb.airrtc.3in1|SoChuang三合一温控器Ultra|34597|
|scdvb.airrtc.3in1v2|SoChuang三合一温控器Ultra|38707|
|scdvb.airrtc.sc8601|Sochuang智能温控器(蓝牙Mesh)|19048|
|scdvb.airrtc.wkq20|SoChuang智能温控器Ultra|27493|
|sfdn.derh.001|先锋耐高温/免倒水除湿机|26560|
|sfdn.derh.21ar|先锋免倒水除湿机CFS60B-21AR|32638|
|sfdn.heater.003|先锋高端全屋暖气片ZY-HN2521RB-28R|30063|
|sfdn.heater.004|先锋高端全屋暖气片电暖器ZY-HD2502RB-22R|30064|
|sfdn.heater.17r|先锋高端全屋暖气片电暖器ZY-HD2506RB-17R|30076|
|sfdn.heater.28r|先锋高端全屋暖气片电暖器ZY-HD2509RB-28R|30077|
|sfdn.heater.yy1r|先锋石墨烯油汀电暖器YY1R|30176|
|shadow.airc.air01|迅透智能户外空调|24586|
|shc.diffuser.s07|特莱香薰机|23596|
|shinef.airfresh.kf900|祥帆新风系统智能控制器|27139|
|shuii.humidifier.jsq001|零雾加湿器|65617|
|shuii.humidifier.jsq002|零雾低温蒸发型加湿器(Ⅱ代）|67078|
|shuse.acpartner.yk13|树色空调伴侣Lite（Mesh）|27613|
|shuse.airm.ss006|树色空气检测仪（BLE）|26193|
|shuse.airm.ss061|树色二氧化碳检测仪（WiFi 6）|36429|
|shuse.airm.ss062|树色甲醛检测仪（WiFi 6）|38877|
|shuse.airm.ss063|树色PM2.5粉尘检测仪（WiFi 6）|39380|
|sixwgh.acpartner.ym01|文光汇空调伴侣（插座款）|35005|
|sixwgh.acpartner.ym02|文光汇空调伴侣（USB款）|35136|
|skyrc.airp.su001|湃妮智能灭菌除臭器 Pro|3559|
|skyrc.airpurifier.pur|湃妮空气净味器|68077|
|slf.aircondition.air03|智拉斐全屏空调控制器（D8）|8961|
|slf.aircondition.air04|智拉斐旋钮空调温控器（HR7）|9332|
|slf.airfresh.airf01|智拉斐全屏新风控制器（D8）|8633|
|slf.airfresh.airf02|智拉斐旋钮新风温控器（HR7）|9334|
|slf.airrtc.air02|智拉斐全屏地暖控制器（D8）|8634|
|slf.airrtc.air05|智拉斐旋钮地暖温控器（HR7）|9333|
|slf.airrtc.temp02|智拉斐三合一温控器|31385|
|solove.fan.f5new|素乐智能风扇F5i|1401|
|suittc.airrtc.6627|SUITTC智能温控器-M1|22585|
|suittc.airrtc.m158|HW 智能温控器 M5|29490|
|suittc.airrtc.m201|HW 智能温控器 M2|26412|
|suittc.airrtc.m301|智能温控器触控版M|17253|
|suittc.airrtc.m302|HW 智能温控器 M1|18128|
|suittc.airrtc.wk168|智能温控器|3110|
|suittc.airrtc.xy001|热炕头温控器|21919|
|suittc.airrtc.xy002|热炕头温控器LCD|23720|
|sumkia.diffuser.zjxxj|绽家精油香薰机|28120|
|sundu.heater.mdrlx|尚度智能室内加热器NPT-QNS2506MDR-LX|29477|
|svamm1.diffuser.aroma1|斯望家居护理香薰机|30643|
|sxzn.airrtc.air01|BONEYLINK三合一温控器|32419|
|symi.airc.air01|亖米空调地暖新风控制器|31466|
|symi.airc.smvrf|亖米VRF中央空调控制器MESH2.0|33499|
|symi.airrtc.nt01|亖米三合一温控器mesh版|18063|
|symi.airrtc.wk01|亖米智能温控器|25437|
|syzn01.airrtc.tc01|CM温控器|20433|
|szdy.airfresh.n80|碧家新风机|1703|
|szhhkj.diffuser.jd01|智能互联香薰机JD01|19565|
|szhhkj.humidifier.h3pro|太空玩家智能无线加湿器J3Pro|32535|
|szlhkj.diffuser.g20|GL智能香薰机(BLE)|37560|
|szmq.airc.znkt02|麦克维尔智能空调|80632|
|szmq.airfresh.xfj01|麦克维尔新风机(MC327)|80611|
|szmq.airfresh.xfj02|麦克维尔调湿新风机(MC330B)|80613|
|sznl.airrtc.rlwk|ZHBAI温控器（WiFi）|34937|
|szxzh.diffuser.jd222|nimin酒店智能香薰机Pro|21763|
|szxzh.diffuser.jd301|AIVI智能香薰机JD系|23029|
|szxzh.diffuser.v03|智能香薰机V系|17998|
|szxzh.fan.f11|AIVI智能循环扇F11Pro|24466|
|szxzh.fan.f12|KeBinsi智能循环扇F12Pro|25321|
|szxzh.fan.f13|KeBinsi智能循环扇F13Pro|25322|
|szxzh.fan.f1x|KeBinsi 智能循环扇 F1 系|38692|
|szxzh.fan.f23|AIVI智能循环扇 F2 系|27224|
|szxzh.fan.f32|nimin多功能涡轮风扇 F3 系|27221|
|szxzh.fan.f33|AIVI智能循环扇F系|26803|
|szxzh.fan.f52|Hoswn智能循环扇 F52Pro|25704|
|szxzh.fan.f53|AIVI智能循环扇F53Pro|25331|
|szxzh.fan.f55|Hoswn智能循环扇 F55Pro|25300|
|szxzh.fan.f77|AIVI智能循环扇 F7系|31255|
|szxzh.fan.f88|AIVI智能循环扇 F8系|33491|
|szxzh.fan.f99|AIVI智能循环扇 F99Pro|34296|
|szxzh.humidifier.js01|KeBinSi智能加湿器 JS01|27830|
|szxzh.humidifier.js01p|KeBinSi智能加湿器JS01P|33070|
|szxzh.humidifier.js02|AIVI 智能加湿器JS02|29639|
|szxzh.humidifier.js03|AIVI 智能加湿器JS03|30913|
|tafiq.fan.c1|塔菲克智能风扇|35908|
|tafiq.fan.s26pro|塔菲克智能桌面风扇S26PRO|37333|
|tafiq.fan.s6pro|塔菲克摇头循环风扇S6PRO|36091|
|telin.airrtc.tlwkq|TLECO温控器|32496|
|telin.airrtc.tlwkq1|TL温控器|37907|
|teruns.humidifier.zyjs|特润斯中央智慧加湿系统|10336|
|tms.fan.ftx23a|沙伯AI负离子空气循环扇|25485|
|tms.heater.sbqnq|沙伯暖风机|29410|
|tnkq.airfresh.tnkq01|童年空气智能康养新风|6287|
|tofan.airc.air|YOOMI空调控制器MESH2.0|27400|
|tofan.airc.air01m|悠觅空调地暖新风控制器|34098|
|tofan.airc.air02|悠觅VRF空调控制器MESH2.0|29729|
|tofan.airc.dlair|悠觅空调地暖控制器|34330|
|tofan.airrtc.wk01|YOOMI三合一温控器MESH2.0|24604|
|tsd.airp.hmng01|通士达净棠空气净化器K1|8003|
|tsd.airp.hmng02|通士达净棠空气净化器K2|8560|
|uvfive.fan.sunny|FIVEHOME智能空气循环扇|11786|
|uwize.airrtc.yzw02|UWIZE优智者三合一旋钮屏温控面板|32900|
|viomi.airc.m1|meekee 1P|2981|
|viomi.airc.m2|meekee 1.5P|2982|
|viomi.airc.m3|meekee 2P|2983|
|viomi.airc.m4|meekee 3P|2984|
|viomi.airc.sd26|云米AI空调 Smart 2S 1.5P (新一级)|17565|
|viomi.airc.sd28|云米AI空调 Super 3柜机3P (新一级)|17568|
|viomi.airc.sd34|云米AI空调Super 3 Max 1.5P（超一级）|24229|
|viomi.airc.sd35|云米AI空调Super 2 1.5P（超一级）|24230|
|viomi.airc.sd36|云米AI空调Smart 3 Max 2P（新一级）|24232|
|viomi.airc.sd37|云米AI空调 Smart 3 1.5P 新1级|24253|
|viomi.airc.y119|Smart AC A2 Pro-18K|18269|
|viomi.aircondition.sd01|Space E 1.5P(新版)|10724|
|viomi.aircondition.sd02|Space X 1.5P(新版)|10725|
|viomi.aircondition.sd03|Smart 2S 新版|10695|
|viomi.aircondition.sd06|Super 2S (除菌版) 1P|10736|
|viomi.aircondition.sd07|Super 2S (除菌版) 1.5P|10737|
|viomi.aircondition.sd08|Smart 2S (除菌版) 2P|10727|
|viomi.aircondition.sd09|Smart 2S (除菌版) 3P|10728|
|viomi.aircondition.sd10|Super 2 (柜式柔风版) 2P|10699|
|viomi.aircondition.sd11|Super 2 (柜式柔风版) 3P|10700|
|viomi.aircondition.sd12|Smart 2 Max 新版|10722|
|viomi.aircondition.sd15|Super 2 (语音版) 1P|10877|
|viomi.aircondition.sd16|Super 2 (语音版) 1.5P|10878|
|viomi.aircondition.sd17|Super 2 Pro（除菌版）1.5P|11015|
|viomi.aircondition.sd18|Smart 2（除菌版）2P|11013|
|viomi.aircondition.sd19|Smart 2（除菌版）3P|11014|
|viomi.aircondition.sd22|Super 3 1.5P|16616|
|viomi.aircondition.sd23|Super 3 2P|16618|
|viomi.aircondition.sd24|云米AI空调 Super 3 Pro 1.5P（新一级）|16619|
|viomi.aircondition.v10|Royal Pro(AI语音人感版)|1587|
|viomi.aircondition.v21|Crown-22A|1736|
|viomi.aircondition.v22|Crown-28A|1735|
|viomi.aircondition.v23|Crown-36A|1734|
|viomi.aircondition.v24|Crown-56A|1733|
|viomi.aircondition.v25|Crown-71A|1731|
|viomi.aircondition.v26|King Pro(AI空净版)|1732|
|viomi.aircondition.v28|Royal(AI语音版) 2P|2310|
|viomi.aircondition.v29| Royal(AI语音版) 3P|2312|
|viomi.aircondition.v30|King Pro-A （AI空净版）|2313|
|viomi.aircondition.v31|King 1S(AI柔风版) 1.5P|2314|
|viomi.aircondition.v32|King  1X 1P|2301|
|viomi.aircondition.v33|King  1X 1.5P|2302|
|viomi.aircondition.v34| King 1A 1P|2315|
|viomi.aircondition.v35| King 1A 1.5P|2316|
|viomi.aircondition.v37|Crown-72A3|5976|
|viomi.aircondition.v38|Crown-26A3|6605|
|viomi.aircondition.v39|Crown-35A3|6606|
|viomi.aircondition.v40|Crown-50A3|6607|
|viomi.aircondition.v6|King(1P)|1590|
|viomi.aircondition.v7|King|1589|
|viomi.aircondition.v8|King 1S(AI柔风版)|1565|
|viomi.aircondition.v9|Royal（AI语音版）|1588|
|viomi.aircondition.y1|Milano（柜式 柔风版）2P|2317|
|viomi.aircondition.y10|Milano 1.5P|2319|
|viomi.aircondition.y101|Milano 2S 1.5P|7195|
|viomi.aircondition.y103|Milano 2T 1.5P|7235|
|viomi.aircondition.y11|iCool 1C 1P|2320|
|viomi.aircondition.y12|iCool 1C 1.5P|2321|
|viomi.aircondition.y13|iCool 1P|2322|
|viomi.aircondition.y14|iCool 1.5P|2323|
|viomi.aircondition.y15|iCool 1S 1.5P|2438|
|viomi.aircondition.y2|Milano（柜式 柔风版）3P|2318|
|viomi.aircondition.y25|iCool 1V 1.5P|3094|
|viomi.aircondition.y26|iCool 1N 1.5P|3095|
|viomi.aircondition.y27|Milano 1N 1P|3130|
|viomi.aircondition.y28|Milano 1N 1.5P|3131|
|viomi.aircondition.y29|iCool 1S 1P(新能效)|3219|
|viomi.aircondition.y3|Milano（柜式）2P|2324|
|viomi.aircondition.y30|iCool 1S 1.5P(新能效)|3220|
|viomi.aircondition.y31|iCool 1P(新能效)|3227|
|viomi.aircondition.y32|iCool 1.5P(新能效)|3228|
|viomi.aircondition.y33|iCool 1H 1P|3319|
|viomi.aircondition.y34|iCool 1H 1.5P|3320|
|viomi.aircondition.y35|iCool 1R 1P|3321|
|viomi.aircondition.y36|iCool 1R 1.5P|3322|
|viomi.aircondition.y37|Milano 1C 2P(新能效)|3323|
|viomi.aircondition.y38|Milano 1C 3P(新能效)|3324|
|viomi.aircondition.y4|Milano（柜式）3P|2325|
|viomi.aircondition.y43|Smart 1S 1P|3346|
|viomi.aircondition.y44|Smart 1S 1.5P|3347|
|viomi.aircondition.y45|Smart 1C 1P|3348|
|viomi.aircondition.y46|Smart 1C 1.5P|3349|
|viomi.aircondition.y47|Smart 1X 1P|3350|
|viomi.aircondition.y48|Smart 1X 1.5P|3351|
|viomi.aircondition.y49|Smart 1P|3352|
|viomi.aircondition.y5|Milano 1S（柔风版）1P|2300|
|viomi.aircondition.y50|Smart 1.5P|3353|
|viomi.aircondition.y51|iCool 2P|3354|
|viomi.aircondition.y52|iCool 3P|3355|
|viomi.aircondition.y53|Navi（柜式 柔风版）2P|3374|
|viomi.aircondition.y54|Navi（柜式 柔风版）3P|3375|
|viomi.aircondition.y55|Navi 1P|3432|
|viomi.aircondition.y56|Navi 1.5P|3433|
|viomi.aircondition.y57|Smart 2P|3434|
|viomi.aircondition.y58|Smart 3P|3435|
|viomi.aircondition.y59|Smart 1X 2P|3436|
|viomi.aircondition.y6|Milano 1S（柔风版）1.5P|2303|
|viomi.aircondition.y60|Smart 1X 3P|3438|
|viomi.aircondition.y64|Navi 2 1P|4502|
|viomi.aircondition.y65|Navi 2 1.5P|4503|
|viomi.aircondition.y66|iCool 2 Max 2P|4538|
|viomi.aircondition.y67|Milano 2 1P|4631|
|viomi.aircondition.y68|Milano 2 1.5P|4632|
|viomi.aircondition.y69|Space X 1.5P|4633|
|viomi.aircondition.y7|Milano（柔风版）1P|2326|
|viomi.aircondition.y71|Space E 1.5P|4768|
|viomi.aircondition.y72|Smart 2 1P|4823|
|viomi.aircondition.y73|Smart 2 1.5P|4824|
|viomi.aircondition.y74|Smart 2 Max 2P|4904|
|viomi.aircondition.y75|Smart 2A|4967|
|viomi.aircondition.y76|Smart 2A|4971|
|viomi.aircondition.y78|Smart 2C 1.5P|4988|
|viomi.aircondition.y79|Milano 2 Pro 1P|5035|
|viomi.aircondition.y8|Milano（柔风版）1.5P|2327|
|viomi.aircondition.y80|Milano 2 Pro 1.5P|5036|
|viomi.aircondition.y81|Smart 2C 1P|5174|
|viomi.aircondition.y82|Smart 2C 1.5P|5175|
|viomi.aircondition.y83|Navi 2 2P|5176|
|viomi.aircondition.y84|Navi 2 3P|5177|
|viomi.aircondition.y85|Navi 2C 2P|5178|
|viomi.aircondition.y86|Navi 2C 3P|5179|
|viomi.aircondition.y88|Smart AC A1-12K|5931|
|viomi.aircondition.y89|Smart AC A1-18K|5932|
|viomi.aircondition.y9|Milano 1P|2328|
|viomi.aircondition.y99|Smart 2S 1.5P|7161|
|viomi.airpurifier.v1|云米互联网空气消毒机|69360|
|viomi.airpurifier.v2|云米互联网空气净化器|69361|
|viomi.fan.v13|云米AI负离子空气循环扇|9151|
|viomi.fan.v5|云米互联网蝶翼仿生电风扇(变频版)|69314|
|viomi.fan.v6|云米互联网空气循环扇|4529|
|viomi.fan.v7|云米互联网直流变频落地扇3|4734|
|viomi.heater.v1|云米AI踢脚线电暖器Cross(恒温加湿版)|10917|
|viomi.heater.v10|云米AI石墨烯踢脚线电暖器Smart Pro|10901|
|viomi.heater.v2|云米AI沉浸式移动地暖Master(石墨烯加湿版)|11127|
|viomi.heater.v3|云米互联网立式电暖器（雾化加湿版）|70876|
|viomi.heater.v4|云米互联网踢脚线电暖器Pro2|70931|
|viomi.heater.v6|云米AI踢脚线电暖器|6215|
|viomi.heater.v8|云米AI对流电暖器|6712|
|viomi.heater.vxtj01|云米互联网踢脚线电暖器 Pro|67947|
|viomi.humidifier.h1|coKiing互联网加湿器King|69714|
|wanai.fan.t118|德姆勒电风扇（单冷塔扇）|2648|
|wangao.airp.wg04|WG-06空气净化器|27757|
|wenxi.fan.yd01|早鱼桌面循环风扇|27248|
|wfxx.acpartner.ir01|PIDPRO空调遥控器A2|27956|
|whykid.heater.wk01|whykid暖风机|22747|
|whzk.airrtc.whwkq|WH智能温控器|30769|
|whzk.airrtc.whwkq2|WH智能温控器BGL|37572|
|wiing.acpartner.ym01|AImLbS智能空调伴侣|30466|
|wiing.acpartner.ym02|AImLbS智能空调伴侣USB版|39133|
|woop12.fan.ldcf|DGUK冰冰空调扇F1|25481|
|wsiter.airrtc.v1|wstiter智能温控器|35377|
|wzojdz.acpartner.ktbl|巨欧智能空调伴侣|35078|
|xar.heater.wal1|吾艾灵智能地毯|17646|
|xbldqc.fan.s1|XBL-S1壁挂/桌面折叠风扇|30471|
|xen.diffuser.v8|小耳牛智能香薰机V08|30536|
|xfly.fan.d02|小飞吊扇D02|36312|
|xfocus.airrtc.t10|声必可三合一温控器|31008|
|xhuan.airc.acnew|苏米VRF空调室内机|30268|
|xhuan.airc.air|苏米中央空调控制器Mesh2.0|26368|
|xhuan.airc.b27se|苏米中央空调控制器Pro Mesh2.0|33046|
|xhuan.aircondition.ac01|苏米VRF控制器|6893|
|xhuan.airrtc.rzwk01|苏米趣动屏温控旋钮S1（氟机版）|35166|
|xhuan.airrtc.wk01|苏米温控器Mesh2.0（三合一版）|23698|
|xiaomi.airc.2r09r1|强劲风 风管机 超4匹 超一级能效|34367|
|xiaomi.airc.2r19r1|人感风 双出风 风管机 大4匹 超一级能效|34368|
|xiaomi.airc.3rf1r1|中央空调Pro（适用于米家中央空调）|35098|
|xiaomi.airc.3rf2r2|中央空调Pro 双风轮（适用于中央空调 双风轮）|34970|
|xiaomi.airc.3ysjkk|小米智能空气管理面板Lite 演示|40662|
|xiaomi.airc.ar02kk|风管机Pro 1.5匹 超一级能效|22728|
|xiaomi.airc.ar08r1|强劲风 风管机 超3匹 超一级能效|29888|
|xiaomi.airc.arf1r1|中央空调Pro（适用于米家中央空调）|21479|
|xiaomi.airc.arf2r1|中央空调Pro（适用于米家中央空调）|29930|
|xiaomi.airc.axxxxx|小米智能空气管理面板|22688|
|xiaomi.airc.ayyyyy|小米智能空气管理面板|24786|
|xiaomi.airc.f55ysj|空调 巨省电Pro 柔风版 大1.5匹 超一级能效|34984|
|xiaomi.airc.frlh00|空调 巨省电Pro 柔风版 立式大3匹 超一级能效|34977|
|xiaomi.airc.h09h00|小米空调巨省电 1.5匹 一级 适用米家速冷静|16496|
|xiaomi.airc.h10h00|小米空调巨省电 1匹 一级 适用米家速冷静|20810|
|xiaomi.airc.h10r00|小米空调巨省电 1匹 一级 适用米家速冷静|20811|
|xiaomi.airc.h21h00|空调 上出风Pro 1.5匹 超一级能效|20805|
|xiaomi.airc.h40h00|空调Pro 健康风 1.5匹超一级能效|24477|
|xiaomi.airc.h46h00|空调Pro 人感上出风 1.5匹 超一级能效|25022|
|xiaomi.airc.h65h00|空调 强劲风 至尊版 超1.5匹 超一级能效|35730|
|xiaomi.airc.r09h00|小米空调巨省电 1.5匹 一级 适用米家速冷静|16498|
|xiaomi.airc.r10h00|小米空调巨省电 1匹 一级 适用米家速冷静|20812|
|xiaomi.airc.r24r00|空调 巨省电Pro  1.5匹 超一级能效|19298|
|xiaomi.airc.rr0r00|空调 新风Pro 双出风 立式3匹 超一级能效|18010|
|xiaomi.airc.rr7r00|空调 新风Pro 双出风 立式3匹 超一级能效（冰晶白）|22472|
|xiaomi.airc.rrar00|空调 巨省电Pro 立式3匹 超一级能效|22654|
|xiaomi.airc.rrhr00|新风空调Pro 人感双出风 立式3匹 超一级能效|25711|
|xiaomi.airc.rrrysj|空调 强劲风Pro 至尊版 立式超3匹 超一级能效|35822|
|xiaomi.aircondition.c14|小米巨省电立式空调（3匹/变频/新三级能效）|4117|
|xiaomi.aircondition.c25|米家空调 自然风 立式 3 匹（新一级能效）|8575|
|xiaomi.aircondition.c30|空调 柔风 立式3匹新一级（含速冷静）|11300|
|xiaomi.aircondition.c32|小米巨省电立式空调 （3匹/变频/新一级能效）|11590|
|xiaomi.aircondition.c35|米家新风空调立式（3匹 新一级能效）|13259|
|xiaomi.aircondition.c38|小米巨省电立式空调 （2匹/变频/新一级能效）|13600|
|xiaomi.aircondition.m3|米家空调 自然风 1.5匹 （新一级能效）|8287|
|xiaomi.aircondition.mc9|小米巨省电立式空调（2匹/变频/新三级能效）|3306|
|xiaomi.aircondition.mt0|米家新风空调 （尊享版 1.5匹）|8374|
|xiaomi.aircondition.mt8|小米巨省电空调 （1.5匹/变频/新一级能效）|3682|
|xiaomi.airp.mp4|米家空气净化器 4|13715|
|xiaomi.airp.mp5b|米家空气净化器 5|34032|
|xiaomi.airp.ua1b|米家全效空气净化器 Ultra|20904|
|xiaomi.airp.ua3|米家全效空气净化器 Ultra 增强版|16990|
|xiaomi.airp.ua3a|米家全效空气净化器 Ultra 增强版|26044|
|xiaomi.airp.va2b|米家空气净化器 4 Pro|13232|
|xiaomi.airp.va3a|米家空气净化器 5S|33713|
|xiaomi.airp.va4|米家空气净化器 4 Pro H|12353|
|xiaomi.diffuser.03wh|米家智能香氛机|27590|
|xiaomi.diffuser.xw002|米家智能香氛机|18462|
|xiaomi.fan.p23|米家直流变频两季扇|23697|
|xiaomi.fan.p23w|米家直流变频两季扇|37890|
|xiaomi.heater.ma4|米家石墨烯智能电暖器|16053|
|xiaomi.heater.ma7|米家石墨烯踢脚线电暖器 2|12443|
|xiaomi.heater.ma7s|米家石墨烯踢脚线电暖器 2|20309|
|xiaomi.heater.ma8a|米家石墨烯暖风机|33636|
|xiaomi.heater.ma8b|米家石墨烯暖风机|36641|
|xiaomi.heater.ma9b|米家石墨烯踢脚线电暖器 2 加湿版|36639|
|xiji.heater.rznfj|RONGEO智能暖风机(WiFi)|32207|
|xinji.airrtc.nt01|新极三合一温控器|18064|
|xizhen.airrtc.mi0002|GERLSAIR中央空调控制器|19499|
|xizhen.airrtc.miac01|GERLSAIR中央空调控制器(Pro)|24899|
|xizhen.airrtc.miac02|GERLSAIR 中央空调控制器(Mesh2.0)|31199|
|xl2024.airc.air|Pluslife VRF中央空调控制器|28864|
|xnydz.fan.v1|KFI 智能Ai冷风扇|38294|
|xydq.acpartner.xiya02|希崖空调插座伴侣XyAir|34070|
|yblxsm.diffuser.jd02|YFNSEA智能香薰机 JD02|39266|
|yblxsm.diffuser.t1|YFNSEA智能香薰机 T1|28541|
|yblxsm.diffuser.v12|YFNSEA智能香薰机V12|28795|
|yeelink.airc.vrf1|Yeelight VRF空调控制器|17971|
|yg1.airrtc.tms01|情景智能三合一温控器|34614|
|yier.fan.v1|KIMEEY直流变频落地扇|35135|
|yier.fan.v2|KIMEEY直流变频平面扇|35207|
|yier.fan.v3|KIMEEY直流变频循环扇FS1282-DC|35378|
|yier.fan.v4|KIMEEY变频循环扇FS1012R|35428|
|yifang.fan.yx02|一方智能风扇|14258|
|yj1226.airc.air|今闪空调控制器Mesh2.0|25984|
|yj1226.airc.air01|今闪中央空调内机|28135|
|yj1226.airc.air02|今闪空调室内机控制器|29611|
|yj1226.airrtc.air|今闪VRF空调温控器|22779|
|yj1226.airrtc.temp|今闪三合一温控器MESH2.0|26415|
|ykl.airrtc.air01|晶米智能温控器mesh版|30014|
|ym001.acpartner.wye802|炎米智能空调伴侣|32945|
|ym001.diffuser.ymxxj|炎米智能香氛机|29475|
|ym001.fan.y1lite|炎米智能手持风扇Lite|38198|
|ym001.fan.ym318|炎米智能手持风扇|35872|
|ym001.fan.ym382|炎米智能便携风扇|35873|
|ym001.fan.ymfs1|炎米智能便携循环扇Y1|37857|
|ym001.fan.ymfs2|炎米智能循环扇Y1|37858|
|ym001.fan.ymfsw|炎米智能风扇（WiFi）|27300|
|ym001.heater.ymnfj|炎米智能暖风机|22077|
|yoda.fan.m55|旋风循环扇|14028|
|yodq.humidifier.yo001|YO 加湿器|6432|
|yoohoo.airrtc.wk01|FRFOX-M6智能温控器|24002|
|youmin.acpartner.zhcp01|佑明空调伴侣 ZH-cp01|27496|
|youmin.acpartner.zhcp02|佑明空调伴侣|27392|
|youmin.airrtc.127|佑明中央空调温控器|23997|
|ys2022.diffuser.w7p|馜花语人来亮屏香薰机|25678|
|ytl.airrtc.8921|YaTeLee智能温度控制器|12150|
|yuemee.airm.mhfdv2|霍尼韦尔甲醛监测仪PRO|9837|
|yuemee.airmonitor.mhfd1|霍尼韦尔甲醛监测仪|735|
|yutai.acpartner.ym01|禹泰电工空调伴侣|30736|
|yutai.acpartner.ym02|禹泰电工智能空调助手|30738|
|yyjj.diffuser.ldc|舒柏思智能香薰机(锂电版)|10835|
|yyjj.diffuser.rxjiot|舒柏思智能香薰机|10818|
|yzjkj.acpartner.a3|麒石空调面板遥控器A3|28957|
|yzjkj.acpartner.kta1|麒石空调遥控器A1|27462|
|zdyk.airrtc.wkb01|青玺三合一温控器|39163|
|zh001.fan.zh27|HHGPK智能风扇|36483|
|zh001.fan.zh57|HHGPK智能桌面风扇|36486|
|zh001.fan.zh59|HHGPK桌面循环摇头风扇|37144|
|zh001.humidifier.h10p|HHGPK智能加湿器H10P|32863|
|zh001.humidifier.h20|HHGPK智能加湿器H20|33895|
|zh001.humidifier.h40|HHGPK智能加湿器H40|33007|
|zhhome.fan.m35|智能吊扇M35|17287|
|zhhome.fan.m55|智能循环扇M55|17343|
|zhhome.fan.m65|智能暴风户外风扇M65|20189|
|zhiee.acpartner.ym02|百将空调伴侣|36974|
|zhimi.aircondition.ma3|米家互联网空调（三级能效）|978|
|zhimi.aircondition.v1|智米全直流变频空调|195|
|zhimi.airfresh.ua1|米家新风机C1 80风量|2218|
|zhimi.airp.mea1|米家消毒空气净化器|7978|
|zhimi.airp.mp4|米家空气净化器 4|3678|
|zhimi.airp.rma2|米家空气净化器 4 Lite|9700|
|zhimi.airp.rma3|米家空气净化器 4 Lite|11507|
|zhimi.airp.ua1|米家全效空气净化器 Ultra|9089|
|zhimi.airp.va2|米家空气净化器 4 Pro|4258|
|zhimi.airpurifier.m1|小米空气净化器2代|100|
|zhimi.airpurifier.ma2|小米米家空气净化器2S|590|
|zhimi.airpurifier.mb1|小米空气净化器2S|631|
|zhimi.airpurifier.rma1|米家空气净化器 4 Lite|2728|
|zhimi.airpurifier.v2|小米空气净化器|34|
|zhimi.airpurifier.v3|小米空气净化器|47|
|zhimi.airpurifier.v5|小米空气净化器|80|
|zhimi.airpurifier.v7|小米空气净化器Pro|630|
|zhimi.airpurifier.virtual|小米空气净化器组|154|
|zhimi.airpurifier.vtl_m1|小米空气净化器2代（虚拟）|148|
|zhimi.fan.v2|智米直流变频落地扇|84|
|zhimi.heater.ma2|米家智能电暖器|1325|
|zhimi.heater.ma4|米家石墨烯智能电暖器|5169|
|zjaupu.humidifier.a1|宅鲸净化加湿器|9530|
|zjaupu.humidifier.a2s|宅鲸净化加湿器A2Pro|17806|
|zjaupu.humidifier.c1|宅鲸净化加湿器C1|15666|
|zjcskj.derh.v1|IGJ智能除湿机|37061|
|zsxny.airrtc.zs001|亿富科智能温湿度控制器|23009|
|zw1688.fan.f70|LWU户外风扇|35115|
|zw1688.fan.f80|LWU户外摇头风扇|35537|
|zw1688.fan.lwufs|LWU智能风扇（BLE）|28992|
|zw1688.fan.y08|LWU多功能夹扇Y8|34678|
|zw1688.fan.y12|LWU智能风扇|34382|
|zw1688.fan.y13|LWU智能桌面风扇|35030|
|zw1688.heater.hx3622|XWZW室内加热器HNQ2000|33373|
|zw1688.heater.hys003|XWZW室内加热器|32210|
|zw1688.heater.znnfj|LWU智能暖风机|30527|
|zxd123.acpartner.ym01|Sparkleiot智能空调伴侣|35386|
|zxkj.aircondition.kt22|正熙户外便携空调|9871|
|zyzy1.aircondition.0715|空调|73650|
|zyzy1.aircondition.y712|智能空调|6263|
|zyzy1.fan.y07011|智能米家风扇|73540|
|zzhu.heater.v1|UG雾化壁炉电暖器|37210|

### 路由网关

|model|name|pd_id|
|---|---|---:|
|090615.gateway.ac10|VRF中央空调网关|16704|
|090615.gateway.ktvrf|PTXZN 空调网关(VRF)|9436|
|090615.gateway.of32|OF VRF中央空调网关(Ultra版)|24662|
|090615.gateway.vrfgw|SOCHUANG VRF中央空调控制器|15700|
|baiten.gateway.air02g|贝兴VRF中央空调网关|26315|
|btzn.gateway.306v1|比特306网关|72239|
|btzn.gateway.307v1|比特307网关|71570|
|btzn.gateway.569v1|比特569网关|71368|
|bymiot.gateway.plcv1|未来居PLC网关|81771|
|bymiot.gateway.rcuv1|未来居一体式RCU网关|74652|
|bymiot.gateway.rcuv2|未来居一体式RCU网关pro|77151|
|bymiot.gateway.v1|企业有线智能网关|66799|
|bymiot.gateway.v2|企业有线智能网关2.0版|67898|
|bymiot.gateway.v2pro|未来居有线智能网关2.0升级版|72540|
|bymiot.gateway.v3pro|未来居有线智能网关3.0增强版|6140|
|bymiot.gateway.v3xtr|未来居有线网关3.0Xtr|76578|
|bymiot.gateway.v4|未来居导轨式RCU网关|81393|
|bymiot.gateway.wlmiv1|未来居无线网关mini|10824|
|bymiot.gateway.wlv1|未来居无线智能网关|71814|
|cdn.gateway.wgdg1|西顿舍见PLC网关|77302|
|cgllc.gateway.s1|青萍蓝牙网关|840|
|chuangmi.gateway.720|小白智能中央空调控制器|8808|
|chuangmi.gateway.ipc011|小白摄像机网关|65837|
|hti.gateway.123|123|72793|
|isa.router.mr01hl|华来小方Mesh路由网关|69280|
|klwdz1.gateway.001|VRF空调网关|25729|
|linp.gateway.n2|领普射频网关|1854|
|linp.gateway.pn1|PLC网关|76642|
|linp.gateway.vrf1|领普VRF中央空调控制器|15499|
|lumi.gateway.acn004|Aqara网关 M1S 2022款|73125|
|lumi.gateway.acn008|Aqara 网关 M1S （第二代）|79140|
|lumi.gateway.acn01|Aqara 网关M1S|67014|
|lumi.gateway.aqcn02|Aqara网关E1（青春版）|70246|
|lumi.gateway.aqhm01|Aqara网关|65927|
|lumi.gateway.mcn001|小米智能多模网关2|5338|
|lumi.gateway.mgl03|小米智能多模网关|1111|
|lumi.gateway.sacn01|智能USB墙壁插座面板H1（网关版）|68944|
|lumi.gateway.v1|多功能网关|24|
|lumi.gateway.v2|小米多功能网关|61|
|lumi.gateway.v3|小米多功能网关|109|
|maxi.gateway.ln069g|品达VRF空调控制器WIFI版|25781|
|maxi.gateway.m07|中央空调智能网关|10816|
|mirsz.gateway.ac300g|罗威亚中央空调智能控制器|29151|
|opple.gateway.opgw|OPPLE 双协议智能网关|82351|
|qdhkl.gateway.b18p|中弘VRF空调管理器|9898|
|qdhkl.gateway.b19|VRF中央空调控制器|8493|
|qdhkl.gateway.b19p|中弘VRF中央空调控制器PRO|26144|
|qdhkl.gateway.b19s|中弘VRF中央空调控制器Ultra|28416|
|qdhkl.gateway.b42|中弘两联供空调控制器|27655|
|qdhkl.gateway.ln0586|LONINK VRF空调控制器PRO|13611|
|qdhkl.gateway.lonink|LONINK VRF中央空调控制器|10246|
|qdhkl.gateway.p20|中弘智能VRF空调集中控制器|28336|
|qdhkl.gateway.sim|亖米VRF中央空调控制器|9696|
|qdhkl.gateway.sm|苏米VRF空调网关|9592|
|shjszn.gateway.c1|榉树智能锁网关|406|
|xhuan.gateway.19se|苏米VRF空调网关PRO|30550|
|xiaomi.gateway.hub1|Xiaomi 中枢网关|6482|
|xiaomi.plc.v1|小米电力线wifi扩展器|362|
|xiaomi.repeater.v1|小米Wi-Fi放大器|90|
|xiaomi.repeater.v2|小米Wi-Fi放大器2|367|
|xiaomi.repeater.v3|小米Wi-Fi放大器Pro|466|
|xiaomi.router.cr5508|小米路由器CR5508|74275|
|xiaomi.router.cr6606|小米路由器CR6606|71340|
|xiaomi.router.cr8806|小米路由器CR8806|73299|
|xiaomi.router.cr8808|小米路由器CR8808|73792|
|xiaomi.router.cr8809|小米路由器CR8809|74506|
|xiaomi.router.cr8816|小米路由器CR8806|79186|
|xiaomi.router.cr8819|小米路由器CR8809|79886|
|xiaomi.router.d01|小米路由器Mesh|66123|
|xiaomi.router.lv1|小米路由青春版|105|
|xiaomi.router.lv3|小米路由器R3C|293|
|xiaomi.router.mv1|小米路由器 mini|27|
|xiaomi.router.old15|小米路由器|71544|
|xiaomi.router.r1350|小米路由器4 Pro|67900|
|xiaomi.router.r2100|小米路由器AC2100|67019|
|xiaomi.router.r2350|小米AIoT路由器AC2350|68670|
|xiaomi.router.r3600|小米AIoT路由器AX3600|68418|
|xiaomi.router.r3d|小米路由器HD|454|
|xiaomi.router.r3g|小米路由器3G|459|
|xiaomi.router.r3gv2|小米路由器3G|66733|
|xiaomi.router.r3gv2n|小米路由器3G|67074|
|xiaomi.router.r4|小米路由器4|773|
|xiaomi.router.r4a|小米路由器4A 千兆版|795|
|xiaomi.router.r4ac|小米路由器4A|65971|
|xiaomi.router.r4av2|小米路由器4A 千兆版|76530|
|xiaomi.router.ra50|Redmi路由器AX5 京东云无线宝|71244|
|xiaomi.router.ra67|Redmi路由器AX5|69721|
|xiaomi.router.ra67u|小米路由器RA67|72479|
|xiaomi.router.ra69|Redmi路由器AX6|70056|
|xiaomi.router.ra70|小米路由器AX9000|71226|
|xiaomi.router.ra71|Redmi路由器AX1800|71168|
|xiaomi.router.ra72|小米路由器AX6000|71337|
|xiaomi.router.ra74|Redmi路由器AX5400|72224|
|xiaomi.router.ra80|小米路由器AX3000|72340|
|xiaomi.router.ra80v2|小米路由器AX3000|79824|
|xiaomi.router.ra81|Redmi路由器AX3000|72341|
|xiaomi.router.rb03|Redmi路由器AX6S|73587|
|xiaomi.router.rb04|Redmi电竞路由器AX5400|74834|
|xiaomi.router.rb06|Redmi路由器AX6000|74928|
|xiaomi.router.rb08|Xiaomi HomeWiFi三频Mesh路由器|74521|
|xiaomi.router.rc01|Xiaomi万兆路由器|76608|
|xiaomi.router.rd01|Xiaomi全屋路由|78961|
|xiaomi.router.rd03v2|Xiaomi路由器AX3000T|81666|
|xiaomi.router.rd04|Xiaomi路由器AX1500|78968|
|xiaomi.router.rd15|Xiaomi路由器BE3600 2.5G版|79936|
|xiaomi.router.rd16|Xiaomi路由器BE3600|80031|
|xiaomi.router.rd16bb|Xiaomi路由器BE3600|82326|
|xiaomi.router.rm1800|小米路由器AX1800|68671|
|xiaomi.router.rm2100|Redmi 路由器AC2100|68298|
|xiaomi.router.rmo15|小米路由器|71545|
|xiaomi.router.rp01|Xiaomi全屋路由 BE3600 Pro 网线版-主路由(5口)|81631|
|xiaomi.router.rp02|Xiaomi全屋路由 BE3600 Pro 网线版-主路由(8口)|81740|
|xiaomi.router.rp03|Xiaomi 全屋路由 BE3600 Pro 网线版-子路由|81673|
|xiaomi.router.rp04|Xiaomi路由器BE10000 Pro|81739|
|xiaomi.router.tr606|小米路由器TR606|72538|
|xiaomi.router.v1|小米路由器|26|
|xiaomi.router.v2|小米路由器|89|
|xiaomi.router.v3|小米路由器3|197|
|xiaomi.router.wr30u|小米路由器WR30U|75765|
|xsmart.gateway.plc04|格物PLC中枢网关|18421|
|yeelink.gateway.pro01|Yeelight Pro 网关|72806|
|yeelink.gateway.v1|Yeelight Mesh网关|636|
|yeelink.gateway.va|Yeelight Mesh网关|2783|
|yeelink.gateway.vrf|Yeelight VRF空调网关|17897|
|yj1226.gateway.air02|今闪VRF中央空调控制器ultra|28153|
|yyzhn.gateway.yn181126|朗越智能安防系统|66206|

### 运动健康

|model|name|pd_id|
|---|---|---:|
|17216.magic_touch.d150|乐范魔力贴温情版|719|
|17216.magic_touch.d152|乐范魔力贴四驱版|669|
|17216.massage.6261d|joypal 世爵双机芯6感智能天王椅 Monster联名款|6112|
|17216.massage.6602a|joypal 伯爵筋膜按摩椅 魔声定制版|4531|
|17216.massage.e560|joypal皇爵AI音律按摩椅 Monster魔声定制款|5033|
|17216.massage.ec1266a|一维AI智能按摩椅|885|
|17216.massage.j6261a|joypal AI智享未来按摩椅|3550|
|17216.massage.jp3209|joypal智能AI按摩椅 魔声联名版|2523|
|ai123.magic_touch.xjb1a|TefeishiAPP智能型颈椎按摩仪|5484|
|amtdq.magic_touch.a01|DP.Brother智能颈椎按摩仪A001|28951|
|asp.treadmill.a9|立久佳跑步机|71086|
|asp.treadmill.pbj|立久佳M1跑步机|67681|
|at123.foot_bath.6sb|云尔康足浴按摩器ZYP001|26978|
|at123.foot_bath.zyp003|云尔康足浴按摩器ZYP003|32061|
|bairen.scales.hd01|辉鼎智能体脂秤HD01|19680|
|bairen.scales.hd01a|辉鼎智能体脂秤HD01-A|36042|
|bairen.scales.hd01b|辉鼎智能体脂秤HD01-B|36043|
|bairen.scales.hd01s|辉鼎智能体脂秤HD01|26548|
|bairen.scales.s300|辉鼎智能体脂秤XTEP-S300|34608|
|bairen.scales.s500s|辉鼎智能体脂秤XTEP-S500|37708|
|bairen.scales.s600|辉鼎智能体脂秤XTEP-S600|35431|
|bairen.scales.xtep4|辉鼎智能体脂秤XTEP-S400|32171|
|baobo.scales.001|宝铂智能体脂秤001|18594|
|baobo.scales.003|宝铂智能体脂秤003|19776|
|baobo.scales.0051|Baobo智能体脂秤0051|28249|
|baobo.scales.e0051|Baobo智能体脂秤E0051|29714|
|baobo.scales.e0061|Baobo智能体脂秤E0061|34829|
|baoju.scales.c026|本博家用体脂秤C026|20334|
|beoka.magic_touch.mcute|MINI肌肉按摩器|13598|
|blst.magic_touch.f2pro|智能颈椎按摩仪|9305|
|boro.scales.bl011|宝岚智能体脂秤BL011|37473|
|bwlife.cup.01|黑白生活智能保温杯|16420|
|chaoka.scales.sn01|淑女智能体脂秤SN-01|26797|
|chaoka.scales.sn02|淑女智能体脂秤SN-02|32286|
|codoon.bleshoes.s10k|咕咚智能跑鞋时尚10K|1032|
|codoon.watch.s1|咕咚GPS运动手表S1|1018|
|cym.magic_touch.a12|Muselove按摩护腰带A12|20914|
|degree.lunar.smh013|37度睡眠监测带SMH013|2947|
|deli.scales.le221a|得力智能体脂秤LE221A|38493|
|desay.bleshoes.s311|Ultra Smart智能跑鞋|343|
|deshi8.scales.t600|得适智能体脂秤T600|20818|
|deshi8.scales.t60010|得适智能体脂秤T600-10|27870|
|deshi8.scales.t600d|得适智能体脂秤T600-D|25809|
|deshi8.scales.t600s|得适智能体脂秤T600-D|26601|
|deshi8.scales.t680|得适智能体脂秤T680|22722|
|dgqh.magic_touch.myj02|MONYOE充气按摩颈枕MYJ02|13468|
|dtr.magic_touch.211mgr|PGG颈椎按摩仪P5B|2949|
|dtr.magic_touch.p6b|PGG颈椎按摩仪P6|3490|
|dtr.magic_touch.p6c|PGG智能颈椎按摩仪P6|9005|
|dtr.magic_touch.p7|PGG颈椎按摩仪P7|4230|
|duhua.jmprope.55|度华体能管理智能跳绳|13067|
|ecozy.magic_touch.b029|迷你热能筋膜枪|6373|
|feebo.jmprope.fj6151|FEEBO智能计数跳绳|8299|
|fgds.cup.fg01|富光米享保温杯|14759|
|fjrh.massage.rh7600|RH多功能按摩椅|7854|
|frks.scales.f38eb|福瑞康盛智能蓝牙体脂秤F38E-B|28359|
|gswl.magic_touch.x1ngd|HD智能暖宫带N8（BLE）|26064|
|gyao.scales.01|荣钰智能体脂秤01|35118|
|hd699.scales.bf1224|BMBL智能体脂秤BF1224|21640|
|hd699.scales.hd006|HUADI智能体脂秤HD006|28919|
|hengbd.magic_touch.kj01|卢威森AI智能筋膜枪（BLE）|21109|
|hith.foot_bath.mjz1|米家智能升降足浴器|9677|
|hith.foot_bath.q2|HITH智能无线足浴器Q2|66829|
|hmpace.bracelet.v4|小米手环4 NFC|1232|
|hmpace.scales.mibfs|小米体脂秤2|1068|
|hmpace.scales.miscale2|小米体重秤2|1069|
|hmpace.watch.v1|Amazfit智能运动手表|472|
|hnjc.scales.tzc01|多锐智能体脂秤|17914|
|hnjc.scales.tzc03|早鱼智能体脂秤|23361|
|hongli.scales.gn007|宏霖光能体脂秤GN007|19515|
|hsgs.scales.hz1228|沪众智能体脂秤HZ1228|22489|
|hsgs.scales.k01|沪众智能体脂秤K01|36103|
|hsgs.scales.k02|沪众智能体脂秤K02|36104|
|hsgs.scales.s01|沪众智能体脂秤S01|30877|
|hsgs.scales.s02|沪众智能体脂秤S02|30878|
|hsm.walkingpad.c2|海斯曼智能走步机|11377|
|huay.scales.s400|至尊智能体脂秤S400|37486|
|huay.scales.s500|至尊家庭版智慧体脂秤S500|40774|
|hwato.magic_touch.htamq|华佗 随身按摩仪|30295|
|hy001.magic_touch.hyjmq|欧佰络筋膜枪|29099|
|hyl.scales.yf280|易复美智能体脂秤YF280|24743|
|hyyx.massage.s518|席位智能按摩椅JY-740|8778|
|hyyx.massage.xwboo1|席位智能按摩椅|7293|
|ihealth.bpm.kd5907|九安智能血压计|65664|
|iot.magic_touch.m101|智能暖宫腰带M101|14362|
|janshi.magic_touch.g2|G2脊安适颈部按摩器|1424|
|janshi.magic_touch.g20|G20脊安适颈部按摩器|5995|
|janshi.magic_touch.u7p|Jeeback智能肩颈揉捏按摩器|23767|
|janshi.magic_touch.u9p|Jeeback按摩靠枕|23784|
|jare.magic_touch.jr688|佳仁按摩披肩JR-688|17393|
|jare.massage.jre6|佳仁按摩椅JR-E6|9268|
|jare.massage.jrq81u|康佳按摩椅KZ-RH8800|9269|
|jare.massage.rh6687|康佳按摩椅KZ-RH6687|9271|
|jare.massage.rh6699|康佳按摩椅KZ-RH6699|10173|
|jb2004.exbike.jb909|JOYBOLD 魔盒动感单车 智能款|29807|
|jback.magic_touch.e10|脊安适E10眼部按摩器|14152|
|jback.magic_touch.e9|E9 Plus 3D振动眼部按摩仪|10389|
|jback.magic_touch.g3|脊安适G3 Pro智能颈部按摩器|11469|
|jback.magic_touch.g9|腰部按摩器|10372|
|jback.magic_touch.k1pr|脊安适智能颈部按摩器|15465|
|jdjz.magic_touch.v1|京东京造 小云朵智能暖宫腰带|35373|
|jiayu.scales.bc235|AI智能体脂秤PRO|17336|
|jiayu.scales.le5020|BC智能LED心率体脂秤|20609|
|jiayua.scales.adzc07|爱国者智能体脂秤ADZC-1807|32138|
|jiayua.scales.adzc7a|爱国者智能体脂秤ADZC-1807A|36277|
|jiayua.scales.adzc7b|爱国者智能体脂秤ADZC-1807B|36278|
|jieman.magic_touch.fbv1|GAX砭石腰腹部按摩仪|5298|
|jieman.magic_touch.g771|玉百纳多功能颈椎按摩仪|9172|
|jieman.magic_touch.g791|GAX 8D颈椎按摩仪|10934|
|jieman.magic_touch.g792|康多力 8D颈椎按摩仪|10935|
|jieman.magic_touch.gax1|GAX智能颈椎按摩仪|7031|
|jieman.magic_touch.gax2|GAX多功能颈部按摩仪|7230|
|jieman.magic_touch.j001|GAX智能肩颈按摩器J-001|16667|
|jieman.magic_touch.j10|GAX 4D颈椎按摩仪X|13956|
|jieman.magic_touch.j15|GAX 智能肩颈按摩仪|22506|
|jieman.magic_touch.js01|吉舒智能颈椎按摩仪V2|4152|
|jieman.magic_touch.js03|吉舒智能颈椎按摩仪V1|4788|
|jieman.magic_touch.js78|吉舒智能颈椎按摩仪|2088|
|jieman.magic_touch.kdl0|康多力智能颈椎按摩仪V2|4167|
|jieman.magic_touch.kdl2|康多力多功能颈部按摩仪|7803|
|jieman.magic_touch.ms9|康多力智能颈椎按摩仪|3718|
|jieman.magic_touch.n88|GAX 智能暖宫腰带|19614|
|jieman.magic_touch.newf|New for智能颈椎按摩仪|4151|
|jieman.magic_touch.t100|GAX智能头部按摩仪|13213|
|jieman.magic_touch.tfs2|Tefeishi智能颈椎按摩仪V2|4169|
|jieman.magic_touch.tsf1|Tefeishi智能颈椎按摩仪|3936|
|jieman.magic_touch.u1|GAX智能U型按摩器|11752|
|jieman.magic_touch.u101|GAX多功能颈椎按摩枕|12500|
|jieman.magic_touch.u102|GAX智能U型按摩器X|12760|
|jieman.magic_touch.x5b|玉百纳智能颈椎按摩仪|5292|
|jieman.magic_touch.x5u|USK智能颈椎按摩仪|5291|
|jieman.magic_touch.yb1|GAX 4D腰腹按摩器|10005|
|jieman.magic_touch.ys01|雅绅智能颈椎按摩仪|3800|
|jieman.magic_touch.ys02|雅绅智能颈椎按摩仪V2|4168|
|jmdz.scales.jm01|金妙智能体脂秤JM01|29538|
|joypal.massage.jp880|joypal AI 揉腰推背能量椅|16689|
|jwsm.scales.m01|安踏智能体脂秤M01|26142|
|kaifen.scales.kfm02|凯丰智能体脂秤KF-M02|23890|
|kaifen.scales.kfmj01|凯丰智能体脂秤KF-M01|18532|
|kdl.scales.cs204|康德立智能体脂秤CS204|28660|
|koxi68.magic_touch.gs69|GS按摩热敷暖腰带|33716|
|ksmb.treadmill.k12|小金K12跑步机|67188|
|ksmb.treadmill.v1|小金智能折叠跑步机|1011|
|ksmb.treadmill.v2|小金K15跑步机|66491|
|ksmb.walkingpad.v1|WalkingPad走步机|331|
|laiex.magic_touch.lexjm|莱恩希多头筋膜枪（BLE）|25466|
|lang.magic_touch.mp02|BY智能电动按摩器MP02|23378|
|lang.magic_touch.n7|智能颈肩按摩仪N7|19628|
|lefu.scales.cf822|乐福光能体脂秤SE|23915|
|lhang.magic_touch.t3|慢客肩颈抓揉按摩器T3|17169|
|lhang.magic_touch.y5|慢客气动按摩腰带Y5|14613|
|linke.scales.dhsjk1|Yuckin智能体脂秤DHSJK1|29718|
|ljj.walkingpad.m7|立久佳电动走步机M7|81762|
|lot.scales.lt2507|乐天智能体脂秤LT2507|30036|
|maijia.ajh.mj9001|MyJoy智能艾灸仪|6979|
|maiyue.magic_touch.m018|MA018多功能颈椎按摩仪|10394|
|meilen.scales.mtz601|Meilen / 美琳 智能体脂秤MTZ601|17531|
|meilen.scales.mtz606|Meilen美琳智能体脂测量仪|23572|
|mhmy.scales.lpz|蓝胖子智能体脂秤LPZ|27217|
|miaomiaoce.thermo.t01|秒秒测智能体温计|219|
|miaomiaoce.thermo.t11|秒秒测蓝牙电子体温计|3071|
|mijia.watch.n62cg|Xiaomi Watch S3 eSIM|18033|
|mijia.watch.n62lte|Xiaomi Watch S3 eSIM|14732|
|mijia.watch.n62s|Xiaomi Watch S4 Sport|14792|
|mijia.watch.o62|Xiaomi Watch S4|19969|
|mijia.watch.o62lte|Xiaomi Watch S4 eSIM|19970|
|miot.bpm.mmm3|测试认证实验室预封样|76149|
|miwear.watch.o61|Xiaomi Watch 5|22326|
|miwear.watch.o61lte|Xiaomi Watch 5 eSIM|22410|
|miwear.watch.o65|REDMI Watch 5|20266|
|miwear.watch.o65m|REDMI Watch 5 eSIM|20267|
|miwear.watch.o66cn|小米手环10|23034|
|miwear.watch.o66nfc|小米手环10 NFC版|23035|
|miwear.watch.o66tc|小米手环10 陶瓷版|23036|
|miwear.watch.p62lte|Xiaomi Watch S5 eSIM 46mm|28155|
|miwear.watch.p67tc|小米手环10 Pro 陶瓷版|29599|
|miwear.watch.q63|Xiaomi Watch S5|34102|
|miwear.watch.q66cn|小米手环11|34834|
|miwear.watch.q66nfc|小米手环11 NFC版|34835|
|miwear.watch.q66tc|小米手环11 陶瓷版|34836|
|miwear.watch.q66u|小米手环11 全金属版|34838|
|muxnw.magic_touch.m71|慕向宠物舱暖宫带M71|22557|
|mzl001.magic_touch.mzl1|muzhilin智能暖手宝|38661|
|nanzh.scales.50d001|奥克斯智能体脂秤|26538|
|peilin.jmprope.pl08f|蓝牙智慧跳绳|8136|
|pgg.magic_touch.m4|M6 真揉捏颈椎按摩仪|7176|
|pma.magic_touch.bhah63|酷轻松EMS健腹护腰仪|28390|
|pma.magic_touch.hmbd01|酷轻松石墨烯EMS腰腹养护仪|23924|
|pma.magic_touch.ho6001|酷轻松石墨烯多功能手腹养护仪|22686|
|pma.magic_touch.jb01|酷轻松颈部固定器|6830|
|pma.magic_touch.jzho60|酷轻松矫姿按摩坐椅|27918|
|pma.magic_touch.kulaxp|酷轻松肩颈背养护仪|13961|
|pma.magic_touch.l30pro|酷轻松石墨烯颈部固定器|20944|
|pma.magic_touch.pma19|酷轻松石墨烯按摩支撑腰带|31873|
|pma.magic_touch.pmav12|酷轻松石墨烯澎湃热敷护腰带V12|16317|
|pma.magic_touch.qnhf60|酷轻松石墨烯气囊腿部按摩器|25942|
|povit.jmprope.p231|普为特智能蓝牙跳绳|8239|
|qihang.magic_touch.4pro|兔唯乐高背腰部按摩仪|18129|
|qihang.magic_touch.nk01|兔唯乐按摩U型枕U2|17666|
|qihang.magic_touch.nk08|兔唯乐肩颈按摩器|17008|
|qihang.magic_touch.nk8p|兔唯乐肩颈按摩器pro|21030|
|qihang.magic_touch.ty4|兔唯乐腰部按摩器|13948|
|qihang.magic_touch.y4s|兔唯乐腰部按摩器Y4S|30194|
|qihang.magic_touch.y5|兔唯乐颈腰按摩靠枕Y5|24306|
|qihang.magic_touch.y5m|兔唯乐颈腰按摩靠枕Y5M|30149|
|qjkj.cup.qjz001|趣家纯钛智能杯FJ-TA015|16832|
|qushui.massage.my01|8H-AI智能4D按摩椅(全能王子)|19817|
|repor.magic_touch.r1|锐珀尔顽DOU荚护颈枕|6756|
|repor.magic_touch.u7max|锐珀尔空气波全身按摩养生垫|25878|
|rotai.magic_touch.mc06|摩摩哒智能车载腰靠|24375|
|rotai.magic_touch.mc07|摩摩哒气囊按摩腰靠MC07|30185|
|rotai.magic_touch.mc08|摩摩哒气囊按摩腰靠MC08|31643|
|rotai.magic_touch.sx300|摩摩哒智能足底按摩器|1220|
|rotai.magic_touch.sx315|摩摩哒头部按摩器|2873|
|rotai.massage.m600u|摩摩哒M600Ultra全身按摩椅|29455|
|rotai.massage.m660p|摩摩哒M660Pro暖芯椅|15408|
|rotai.massage.m700|摩摩哒M700智能按摩椅|4710|
|rotai.massage.m700a|摩摩哒M700Pro智能按摩椅|6029|
|rotai.massage.rt5728|摩摩哒智能休闲按摩椅Mini|1221|
|rotai.massage.rt5850|按摩椅RT5850|461|
|rotai.massage.rt5850s|摩摩哒休闲按摩椅RT5850S|851|
|rotai.massage.rt5859|小摩侠3D按摩椅|2249|
|rotai.massage.rt5863|摩摩哒智能AI全身按摩椅|923|
|rotai.massage.rt5870|摩摩哒AI全身按摩椅|1222|
|ryeex.bracelet.sake|黑加手环|911|
|shanm.scales.8024c|山盟智能体脂秤8024充电款|37913|
|shanm.scales.8024d|山盟智能体脂秤8024电池款|37912|
|shanm.scales.8024g|山盟智能体脂秤8024光能款|37914|
|shanm.scales.8026c|山盟智能体脂秤8026充电款|40319|
|shanm.scales.8026d|山盟智能体脂秤8026电池款|40320|
|shanm.scales.8026g|山盟智能体脂秤8026光能款|40191|
|shcs.analyzer.20md|百捷血糖尿酸总胆固醇分析仪|17246|
|sic.scales.1300ar|香山家庭用智能体脂秤|18811|
|sic.scales.atz001|沐美智能体脂秤ATZ001|17696|
|sic.scales.m1|香山智能体脂秤|21787|
|sic.scales.mtz200|Meilen智能心率体脂秤|22532|
|skg.magic_touch.skgw50|SKG按摩腰带W5 TE|4794|
|sld001.walkingpad.s2|速立达S2智能走步机|5668|
|sld001.walkingpad.s2pro|速立达S2 Pro智能走步机|9478|
|smg.scales.bt973|早鱼智能体脂秤BT973|18016|
|smooky.jmprope.ts43|Smooky智能跳绳|13137|
|smooky.magic_touch.ma01|SMOOKY智能筋膜枪|15022|
|suzi.scales.a181|苏子智能体脂秤A181|36905|
|suzi.scales.a33|苏子智能体脂秤A33|21391|
|suzi.scales.a35|苏子智能体脂秤A35|24234|
|suzi.scales.a36|苏子智能体脂秤A36|26382|
|suzi.scales.h18|苏子智能体脂秤H18|27054|
|suzi.scales.s400|苏子智能体脂秤S400|37195|
|suzi.scales.s500|苏子智能体脂秤S500|29713|
|suzi.scales.s600|苏子智能体脂秤S600|28224|
|suzi.scales.sz01|苏子智能体脂秤SZ01|30853|
|suzi.scales.sz02|苏子智能体脂秤SZ02|30854|
|suzi.scales.sz04|苏子智能体脂秤SZ04|34432|
|suzi.scales.x600|星秤智能体脂秤X600|34397|
|sxing.scales.a60|时星智能体脂秤A60|26303|
|sxing.scales.a61|时星智能体脂秤A61|26304|
|sxing.scales.s8002|时星智能体脂秤S8002|32462|
|sxing.scales.s8005|时星智能体脂秤S8005|32463|
|sxing.scales.s801|时星智能体脂秤S801|30413|
|sxing.scales.s806|时星智能体脂秤S806|30414|
|thinks.lunar.xm1|智能睡眠传感器Lunar|286|
|trios.bleshoes.v1|米家智能跑鞋|403|
|trios1.bleshoes.rftcdl|赤燚温控鞋左|7938|
|trios1.bleshoes.rftcdr|赤燚温控鞋右|7939|
|trios1.bleshoes.v02|FREETIE运动智芯|660|
|tsec.scales.5049|天晟智能体脂秤FL549|28360|
|tsec.scales.bf669|智能体脂秤|17238|
|tsec.scales.dc549|天晟智能体脂秤DC549|29329|
|tsec.scales.s549|天晟智能体脂秤S549|32211|
|tsec.scales.s649|天晟智能体脂秤S649|32212|
|tstar.magic_touch.6d|康佳智能筋膜枪V19-6D|21154|
|tstar.magic_touch.8x|康佳智能筋膜枪V19-8X|21155|
|tstar.magic_touch.a8|康佳智能筋膜枪|14625|
|tstar.magic_touch.r8|VTT肩颈按摩仪|17211|
|tstar.magic_touch.s6|VTT智能筋膜枪S6|22434|
|tuyi.scales.mx70|途一智能体脂秤MX70|31617|
|umay.treadmill.p|佑美W1 Pro跑步机|4065|
|weik.scales.t2816|唯尚智能健康体脂秤T2816|19079|
|weik.scales.ws2601|唯尚智能健康体脂秤WS2601|24416|
|weik.scales.ws2611|唯尚智能健康体脂秤WS2611|38432|
|weik.scales.ws2901|唯尚智能健康体脂秤WS2901|19912|
|wenxi.scales.01|匹克体脂秤01|30269|
|wenxi.scales.m02|早鱼智能体脂秤M02|24450|
|whx.magic_touch.11|带趣智能暖宫腰带|14340|
|whx.magic_touch.nuanwe|带趣智能护胃带|14341|
|whx.magic_touch.yanbao|带趣智能护眼宝|14342|
|wiseda.scales.m01|蓝牙智能体脂秤M01|20315|
|wiseda.scales.m02|蓝牙智能体脂秤M02|21005|
|wiseda.scales.pro|蓝牙智能体脂秤M03|20316|
|wjh.magic_touch.p1|伟伽桦智能捶打披肩|9485|
|wjh.magic_touch.yb01|伟伽桦智能眼部按摩仪|9484|
|wliot.scales.fg2009|沃莱智能体脂秤小魔瘦[FG2009B]|14623|
|wok.scales.km2014|艾斯凯智能体脂秤KM-2014|40101|
|wok.scales.km2030|艾斯凯智能体脂秤KM-2030|40102|
|wole.scales.01c|如一智能体脂秤RY01C|28948|
|wole.scales.mjh04|如一智能体脂秤MJH-04|35288|
|wole.scales.mjh05|如一智能体脂秤MJH-05|35289|
|wole.scales.ry01|如一智能体脂秤RY01|29150|
|xiaomi.foot_bath.mizs1|米家智能杀菌足浴器|13223|
|xiaomi.foot_bath.mizs3|米家智能杀菌足浴器|33671|
|xiaomi.magic_touch.jj02|米家智能肩颈按摩仪|33724|
|xiaomi.magic_touch.jz01|米家智能颈枕按摩仪|22692|
|xiaomi.magic_touch.jz02|米家智能颈枕按摩仪|33726|
|xiaomi.magic_touch.my03|米家智能眼部按摩仪|33722|
|xiaomi.magic_touch.tbs4|米家智能头部按摩梳 流金钛|33669|
|xiaomi.magic_touch.tbsh|米家智能头部按摩梳 琥珀红|30119|
|xiaomi.magic_touch.tbsz|米家智能头部按摩梳 罗勒紫|27269|
|xiaomi.magic_touch.yb03|米家智能腰部按摩仪|33774|
|xiaomi.magic_touch.yz02|米家智能按摩眼罩|33725|
|xiaomi.watch.band1A|小米手环|296|
|xiaomi.watch.band1S|小米手环|295|
|xiaomi.watch.band2|小米手环|294|
|xiaoxun.ro_skates.v1|小寻智能轮滑鞋|891|
|xiaoxun.watch.sw306|小寻儿童电话手表A3|66212|
|xiaoxun.watch.sw705|小寻儿童电话手表Y1|66215|
|xiaoxun.watch.sw710a2|小寻儿童电话手表X1|832|
|xiaoxun.watch.sw900|小寻AI学习手表MAX Pro|68686|
|xiaoxun.watch.v1|米兔手表|170|
|xiaoxun.watch.v10|小寻儿童电话手表F2|813|
|xiaoxun.watch.v2|小寻手表 彩屏版|376|
|xiaoxun.watch.v4|小寻儿童电话手表T1|421|
|xiaoxun.watch.v5|小寻儿童电话手表S1|572|
|xiaoxun.watch.v7|小寻儿童电话手表A2|675|
|xiaoxun.watch.v8|小寻儿童电话手表F1|674|
|xnydz.scales.fl7022|KFI智能体脂秤FL7022|39771|
|xqiao.treadmill.q2pro1|小乔跑步机Q2 pro|15342|
|xqiao.treadmill.q3pro|小乔跑步机Q3 pro|28618|
|xqiao.treadmill.srpro1|小乔跑步机SR pro|15027|
|xsdz.scales.if1133|香山智能体脂秤M2|29870|
|xsdz.scales.if1134|香山智能体脂秤M3|29871|
|xshui.scales.m001|爱鱼智能体脂秤M-001 充电款|39123|
|ybb.magic_touch.jz|颈椎按摩仪|15041|
|ybb.magic_touch.ms|眼部按摩仪|7699|
|ybb.magic_touch.znpj01|肩颈按摩器N5|19755|
|ybb.massage.jxs|AI智能按摩椅|9715|
|ybb.massage.ms|智能按摩椅|8193|
|ybsm.scales.fl649|冒泡堂智能体脂秤FL549|16449|
|ybsm.scales.mpt992|冒泡堂智能体脂秤MPT992|20261|
|yier.foot_bath.znzyq|KIMEEY智能足浴器|30326|
|yktime.scales.zshz1|致生活智能体脂秤ZSH-Z1|18373|
|yktime.scales.zshz2|致生活智能体脂秤ZSH-Z2|19586|
|ym001.cup.ymdrb|炎米智能电热杯|29899|
|ym001.cup.ymjbb|炎米智能搅拌杯|31814|
|ym001.magic_touch.ybamq|炎米智能腰部按摩仪|32640|
|ym001.magic_touch.ymamq|炎米智能肩颈按摩仪|29711|
|ym001.magic_touch.ymjmq|炎米智能筋膜枪|28439|
|ym001.magic_touch.ymngd|炎米智能暖宫腰带|31562|
|ym001.scales.ym001|炎米智能体脂秤|32101|
|yoda.scales.hd0|辉鼎智能体脂秤HD0|20983|
|yoda.scales.m01|智能体脂秤M01|18412|
|yoda.scales.mx80|途一智能体脂秤MX80|14801|
|yoda.scales.mx81|禾诗智能体脂秤MX81|19479|
|yoda.scales.rq01|若轻智能体脂秤RQ01|18523|
|yoda.scales.xgs001|小怪兽智能体脂秤XGS01|18388|
|yunmai.scales.m1690|云麦好轻mini2智能体脂秤|397|
|yunmai.scales.ms3001|小米八电极体脂秤|9710|
|zchen.scales.km2014|ACK智能体脂秤KM-2014|38097|
|zchen.scales.km2030|ACK智能体脂秤KM-2030|38098|
|zdeer.ajh.4th12|左点小艾4代智能热敷宝Pro|35070|
|zdeer.ajh.a8|左点小艾智能艾灸盒|66596|
|zdeer.ajh.a9|左点小艾2代智能艾灸盒|67103|
|zdeer.ajh.ajb|左点小艾智能暖灸宝|1775|
|zdeer.ajh.zda10|左点小艾2Max|68354|
|zdeer.ajh.zda9|左点小艾2代智能艾灸盒|66759|
|zdeer.ajh.zdl9|左点小艾智能艾灸加热器|68291|
|zdeer.ajh.zdx8|左点小艾智能艾灸加热器X8|69881|
|zdeer.ajh.zjy|左点智能艾蒸器|67391|
|zdeer.foot_bath.zdz7|左点智能足蒸器Z9|70954|
|zdeer.foot_bath.zdz8|左点智能足蒸器Z8|70436|
|zdeer.foot_bath.zdz9|左点智能足蒸器Z9|71587|
|zh001.magic_touch.zhngd|赞禾智能暖宫带|31052|
|zhhome.magic_touch.a9|智能拔罐仪A9|17341|
|zihe.scales.m01s|ZH智能体脂秤M01|26305|
|zihe.scales.zhm01|ZH智能体脂秤M01|25720|
|zihe.scales.zhm02|ZH智能体脂秤M02|25721|
|zimmo.magic_touch.ffv1|智魔智能双蛋足疗机FREEFOOT1.0|14606|
|zjie.scales.adl26m|增杰家用体脂秤ADL-26M|17477|
