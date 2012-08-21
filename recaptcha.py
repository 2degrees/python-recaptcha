################################################################################
#
# Copyright (c) 2012, 2degrees Limited <gustavonarea@2degreesnetwork.com>.
# All Rights Reserved.
#
# This file is part of python-recaptcha <http://packages.python.org/recaptcha>,
# which is subject to the provisions of the BSD at
# <http://dev.2degreesnetwork.com/p/2degrees-license.html>. A copy of the
# license should accompany this distribution. THIS SOFTWARE IS PROVIDED "AS IS"
# AND ANY AND ALL EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT
# NOT LIMITED TO, THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST
# INFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE.
#
################################################################################
"""reCAPTCHA client."""

from json import dumps as json_encode
from urllib import urlencode
from urllib2 import Request
from urllib2 import URLError
from urllib2 import urlopen
from urlparse import urljoin
from urlparse import urlsplit
from urlparse import urlunsplit


__all__ = [
    'RecaptchaClient',
    'RecaptchaException',
    'RecaptchaInvalidChallengeError',
    'RecaptchaInvalidPrivateKeyError',
    'RecaptchaUnreachableError'
    ]


_RECAPTCHA_API_URL = 'http://www.google.com/recaptcha/api/'


_RECAPTCHA_VERIFICATION_RELATIVE_URL_PATH = 'verify'
_RECAPTCHA_JAVASCRIPT_CHALLENGE_RELATIVE_URL_PATH = 'challenge'
_RECAPTCHA_NOSCRIPT_CHALLENGE_RELATIVE_URL_PATH = 'noscript'


_RECAPTCHA_CHALLENGE_MARKUP_TEMPLATE = """
<script type="text/javascript">
    var RecaptchaOptions = {recaptcha_options_json};
</script>
<script
    type="text/javascript"
    src="{javascript_challenge_url}"
    >
</script>
<noscript>
   <iframe
       src="{noscript_challenge_url}"
       height="300"
       width="500"
       frameborder="0"
       >
   </iframe>
   <br />
   <textarea name="recaptcha_challenge_field" rows="3" cols="40"></textarea>
   <input
       type="hidden"
       name="recaptcha_response_field"
       value="manual_challenge"
       />
</noscript>
"""


_CLIENT_USER_AGENT = \
    '2degrees reCAPTCHA Client (https://github.com/2degrees/python-recaptcha)'


class RecaptchaClient(object):
    
    def __init__(
        self,
        private_key,
        public_key,
        recaptcha_options=None,
        verification_timeout=None,
        ):
        super(RecaptchaClient, self).__init__()
        
        self.private_key = private_key
        self.public_key = public_key
        
        self.recaptcha_options_json = json_encode(recaptcha_options or {})
        
        self.verification_timeout = verification_timeout
    
    def get_challenge_markup(
        self,
        was_previous_solution_incorrect=False,
        use_ssl=False,
        ):
        challenge_markup_variables = {
            'recaptcha_options_json': self.recaptcha_options_json,
            }
        
        challenge_urls = self._get_challenge_urls(
            was_previous_solution_incorrect,
            use_ssl,
            )
        challenge_markup_variables.update(challenge_urls)
        
        challenge_markup = _RECAPTCHA_CHALLENGE_MARKUP_TEMPLATE.format(
            **challenge_markup_variables
            )
        return challenge_markup
    
    def is_solution_correct(self, solution_text, challenge_id, remote_ip):
        if not solution_text or not challenge_id:
            return False
        
        verification_result = self._get_recaptcha_response_for_solution(
            solution_text,
            challenge_id,
            remote_ip,
            )
        
        is_solution_correct_ = verification_result['is_solution_correct']
        
        if not is_solution_correct_:
            error_code = verification_result['error_code']
            if error_code == 'invalid-request-cookie':
                raise RecaptchaInvalidChallengeError(challenge_id)
            elif error_code == 'invalid-site-private-key':
                raise RecaptchaInvalidPrivateKeyError(self.private_key)
        
        return is_solution_correct_
    
    def _get_challenge_urls(
        self,
        was_previous_solution_incorrect,
        use_ssl,
        ):
        url_query_components = {'k': self.public_key}
        if was_previous_solution_incorrect:
            url_query_components['error'] = 'incorrect-captcha-sol'
        url_query_encoded = urlencode(url_query_components)
        
        javascript_challenge_url = _get_recaptcha_api_call_url(
            use_ssl,
            _RECAPTCHA_JAVASCRIPT_CHALLENGE_RELATIVE_URL_PATH,
            url_query_encoded,
            )
        
        noscript_challenge_url = _get_recaptcha_api_call_url(
            use_ssl,
            _RECAPTCHA_NOSCRIPT_CHALLENGE_RELATIVE_URL_PATH,
            url_query_encoded,
            )
        
        challenge_urls = {
            'javascript_challenge_url': javascript_challenge_url,
            'noscript_challenge_url': noscript_challenge_url,
            }
        return challenge_urls
    
    def _get_recaptcha_response_for_solution(
        self,
        solution_text,
        challenge_id,
        remote_ip,
        ):
        verification_url = _get_recaptcha_api_call_url(
            _RECAPTCHA_VERIFICATION_RELATIVE_URL_PATH,
            use_ssl=True,
            )
        request_data = urlencode({
            'privatekey': self.private_key,
            'remoteip': remote_ip,
            'challenge': challenge_id,
            'response': solution_text,
            })
        request = Request(
            url=verification_url,
            data=request_data,
            headers={'User-agent': _CLIENT_USER_AGENT},
            )
        
        urlopen_kwargs = {}
        if self.verification_timeout is not None:
            urlopen_kwargs['timeout'] = self.verification_timeout
        try:
            response = urlopen(request, **urlopen_kwargs)
        except URLError, exc:
            raise RecaptchaUnreachableError(exc)
        else:
            response_lines = response.read().splitlines()
            response.close()
        
        is_solution_correct = response_lines[0] == 'true'
        verification_result = {'is_solution_correct': is_solution_correct}
        if not is_solution_correct:
            verification_result['error_code'] = response_lines[1]
        
        return verification_result


#{ Exceptions


class RecaptchaException(Exception):
    """Base class for all reCAPTCHA-related exceptions."""
    pass


class RecaptchaInvalidPrivateKeyError(RecaptchaException):
    pass


class RecaptchaInvalidChallengeError(RecaptchaException):
    pass


class RecaptchaUnreachableError(RecaptchaException):
    pass


#{ Utilities


def _get_recaptcha_api_call_url(use_ssl, relative_url_path, encoded_query=''):
    url_scheme = 'https' if use_ssl else 'http'
    
    recaptcha_api_url_components = urlsplit(_RECAPTCHA_API_URL)
    url_path = urljoin(
        recaptcha_api_url_components.path,
        relative_url_path,
        )
    
    url = urlunsplit((
        url_scheme,
        recaptcha_api_url_components.netloc,
        url_path,
        encoded_query,
        '',
        ))
    return url


#}