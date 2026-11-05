"""Conservative non-physical offer decisions, with archived source facts."""
import re
from copy import deepcopy

MODEL = re.compile(r'[A-Za-z]|\d|[零一二三四五六七八九十]+代|型号|款')
OTHER = ('延保服务', '上门清洗', '检测服务', '拆旧费', '上门勘测服务', '上门维修', '清洁保养服务', '清洁保养套装服务', '屏幕换新服务', '后盖换新服务', '勘测服务')
PREORDER = re.compile(r'定金|订金|权益|预约|盲约|预售|占位|不发货')
# Remove descriptions of included benefits, negations and appliance timer features
# before matching. Keep the original spelling of the remaining evidence.
DESCRIPTIONS = re.compile(
    r'(?:含|赠送|附赠|赠|送)(?:免费)?(?:安装服务|安装|延保服务|延保|上门服务|上门安装|以旧换新补贴|充值卡|贴膜服务|权益)(?:\d+年)?'
    r'|(?:无需|免|非|不是|不收|无需支付)(?:定金|订金|预约|预售)'
    r'|(?:\d+\s*小时|定时|智能|支持)(?:预约)(?:功能)?'
    r'|预约(?:功能|定时|开关|煮饭|烹饪|煮粥)|权益保障|占位(?:检测|传感器)'
    r'|送货上门|配送上门|含上门|赠上门')


def evidence(reason, word, basis='name'):
    return dict(reason=reason, basis=basis, matched=word,
                matched_rule=reason.split(':')[0], matched_text=word)


def classify_non_goods(row):
    name = DESCRIPTIONS.sub('', str(row.get('name') or '').strip())
    # A concrete delivery lead time on a physical SKU is not a deposit offer.
    if row.get('record_level') == 'sku' and row.get('sku_no') and row.get('specs'):
        name = re.sub(r'预售\s*\d+\s*天', '', name)
    match = PREORDER.search(name)
    if match:
        return evidence('preorder_deposit', match.group())
    return classify_service(row)


def classify_service(row):
    name = str(row.get('name') or '').strip()
    # Product descriptions and bundles must never establish a service identity.
    if re.search(r'免安装|安装尺寸|安装套件|安装组件|赠|附赠|含安装|送安装', name):
        return None
    name = DESCRIPTIONS.sub('', name)
    for word in ('安装服务', '安装调试', '上门安装'):
        if word in name:
            return evidence('service:installation', word)
    if name.endswith('安装') and not MODEL.search(name[:-2]):
        return evidence('service:installation', '安装', 'name_suffix_without_model')
    for word in OTHER:
        if word in name:
            return evidence('service:other', word)
    for word in ('延保', '上门', '以旧换新补贴', '充值卡', '贴膜服务'):
        if word in name:
            return evidence('service:other', word)
    return None


def plan_services(rows, archive):
    kept = []
    archived = {r['id']: deepcopy(r) for r in archive}
    for row in rows:
        from goodsdex.price_semantics import name_kind
        partial = row.get('price_kind') in ('deposit', 'upgrade_diff', 'bundle_extra') or name_kind(row)[0]
        decision = None if partial else classify_non_goods(row)
        if decision:
            archived.setdefault(row['id'], deepcopy(row))
        else:
            kept.append(row)
    return kept, list(archived.values())
