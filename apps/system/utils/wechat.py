from system.models import WechatConfig


def get_wechat_config(sys_id: int, wxa_aid: str = '', mp_aid: str = '', mch_api_key: str = ''):
    qs = WechatConfig.objects.filter(system__sys_id=sys_id, is_default=True)
    if wxa_aid:
        config = qs.filter(wxa_aid=wxa_aid).order_by('create_time').first()
    elif mp_aid:
        config = qs.filter(mp_aid=mp_aid).order_by('create_time').first()
    elif mch_api_key:
        config = qs.filter(mch_api_key=mch_api_key).order_by('create_time').first()
    else:
        config = qs.order_by('create_time').first()
    if config is None:
        raise ValueError('WechatConfig not found!')
    return config
