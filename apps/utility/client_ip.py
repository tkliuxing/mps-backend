"""
获取真实客户端IP
"""

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    x_real_ip = request.META.get('HTTP_X_REAL_IP')
    if x_forwarded_for:
        # 如果请求经过代理，HTTP_X_FORWARDED_FOR中会包含客户端的真实IP
        ip = x_forwarded_for.split(',')[0].strip()
    elif x_real_ip:
        ip = x_real_ip
    else:
        # 否则，使用REMOTE_ADDR作为客户端IP
        ip = request.META.get('REMOTE_ADDR')
    return ip
