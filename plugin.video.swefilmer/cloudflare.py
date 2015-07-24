""" Module to bypass cloudflare's "I'm Under Attack Mode"

Tries to make a request, and if a 503 response is returned
Calculate the javascript challenge to get the clearance cookie.
"""
import urllib2

def add(l, r):
    return parse_aritmetic_string(l) + parse_aritmetic_string(r)


def mult(l, r):
    return parse_aritmetic_string(l) * parse_aritmetic_string(r)


def parse_aritmetic_string(s):
    p_pos = s.find('+')
    m_pos = s.find('*')
    if p_pos == -1 and m_pos == -1:
        return int(s)
    if p_pos == -1:
        return mult(s[0:m_pos], s[m_pos + 1:])
    return add(s[0:p_pos], s[p_pos + 1:])


def calc_jschl_answer(html):
    s = 'swefilmer.com'
    a_start = html.find('a.value')
    expr = html[a_start + 10:html.find(';', a_start)]
    res = parse_aritmetic_string(expr)
    return res + len(s)


def get_form_values(html):
    action_url_start = html.find("action=\"") + 8
    action_url_end = html.find("\"", action_url_start + 1)
    action_url = html[action_url_start:action_url_end]

    a = 'name="jschl_vc" value="'
    vc_value_start = html.find(a) + len(a)
    vc_value_end = html.find('"', vc_value_start)
    vc_value = html[vc_value_start:vc_value_end]

    return action_url, vc_value


def cf_get_url(url, js_answer, vc_value):
    return '%s?jschl_vc=%s&jschl_answer=%s' % (url, vc_value, js_answer)


class NoRedirectHandler(urllib2.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, hdrs, newurl):
        pass  # Disable redirect


def cloudflare_clearance(cf_content, cfduid_cookie):
    js_answer = calc_jschl_answer(cf_content)
    url, vc = get_form_values(cf_content)
    url_with_query = cf_get_url(url, js_answer, vc)

    headers = {
        'Cookie': cfduid_cookie,
        'User-agent': 'curl/7.30.0'
    }
    req = urllib2.Request('http://www.swefilmer.com' + url_with_query,
                          headers=headers)
    try:
        # Build custom opener with a redirect handler
        # This gives us a chance to get the cookie
        opener = urllib2.build_opener(NoRedirectHandler)
        opener.open(req).read()
    except Exception, e:
        # Get clearance cookie
        cookie = e.headers.getheader('Set-Cookie').split(';')[0]
        return cookie
