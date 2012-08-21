***********************
reCAPTCHA Python client
***********************

.. module:: recaptcha

:Latest release: |release|
:Download: `<http://pypi.python.org/pypi/recaptcha/>`_
:Development: `<https://github.com/2degrees/python-recaptcha>`_
:Author: `2degrees Limited <http://dev.2degreesnetwork.com/>`_

This is a pythonic and well-documented `reCAPTCHA
<https://www.google.com/recaptcha/>`_ client that supports all the features of
the remote API to generate and verify CAPTCHA challenges.

The library requires Python 2.6 (or newer) and has no external dependencies.

`Mailhide <http://www.google.com/recaptcha/mailhide/>`_ support is outside the
scope of the project.

Tutorial
========

Firstly, you need to initialize the client::

    from recaptcha import RecaptchaClient
    recaptcha_client = RecaptchaClient('private key', 'public key')

The client is stateless, so it's absolutely fine to create it once and reuse it
as many times as you want, even across different threads.

For more information, read the documentation for :class:`RecaptchaClient`.

Generating challenges
---------------------

To generate the markup to present a challenge, you need to use the
:meth:`RecaptchaClient.get_challenge_markup` method::

    >>> print recaptcha_client.get_challenge_markup()
    
    <script type="text/javascript">
        var RecaptchaOptions = {};
    </script>
    <script
        type="text/javascript"
        src="http://www.google.com/recaptcha/api/challenge?k=public+key"
        >
    </script>
    <noscript>
       <iframe
           src="http://www.google.com/recaptcha/api/noscript?k=public+key"
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


If the user failed to enter the correct solution and you need to redisplay the
form with a different challenge, you need to call
:meth:`~RecaptchaClient.get_challenge_markup` with the argument
``was_previous_solution_incorrect`` set to ``True``.

For more information, read the documentation for
:meth:`~RecaptchaClient.get_challenge_markup`.


Verifying solutions
-------------------

To verify the solution to a CAPTCHA challenge, you need to call the
:meth:`RecaptchaClient.is_solution_correct` method. For example::

    try:
        is_solution_correct = recaptcha_client.is_solution_correct(
            'hello world',
            'challenge',
            '192.0.2.0',
            )
    except RecaptchaUnreachableError as exc:
        disable_form(reason='reCAPTCHA is unreachable; please try again later')
    except RecaptchaException as exc:
        report_exception_to_developers(exc)
    else:
        if is_solution_correct:
            accept_form_data()
        else:
            redisplay_form(error='Invalid solution to CAPTCHA challenge')

For more information, read the documentation for
:meth:`~RecaptchaClient.is_solution_correct`.


Client API
==========

.. autoclass:: RecaptchaClient

Exceptions
----------

.. autoexception:: RecaptchaException

.. autoexception:: RecaptchaInvalidChallengeError

.. autoexception:: RecaptchaInvalidPrivateKeyError

.. autoexception:: RecaptchaUnreachableError


Support
=======

For general reCAPTCHA support, please visit the `reCAPTCHA developers' site
<https://developers.google.com/recaptcha/>`_.

For suggestions and questions about the library, please use our `2degrees-floss
mailing list <http://groups.google.com/group/2degrees-floss/>`_.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

