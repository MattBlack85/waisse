# -*- coding: utf-8 -*-
import json
import os
import re
from pathlib import Path

import requests

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))


class APIClient:
    actions_mapping = {
        'post': 'create',
        'get': 'get',
        'delete': 'delete',
        'put': 'update'
    }
    json_header = {'Content-Type': 'application/json'}
    base_auth_header = {'Authorization': 'Token %s'}
    login_uri = 'login'
    logout_uri = 'logout'
    refresh_token_uri = 'refresh_token'

    def __init__(self):
        _, _, self.os_user, *_ = os.getcwd().split('/')  # Get the actual OS user
        self.path = '/home/%s/.waisse' % self.os_user
        self.session_folder = Path(self.path)
        self.credentials_file = self.session_folder / 'storage'
        self.config = json.loads(
            open(os.path.join(THIS_FOLDER, '..', 'config.json'), 'rb').read().decode()
        )
        self.version = self.config['version']
        self.endpoints = self.config['endpoints']
        self.subdomain = self.config['subdomain']
        self.protocol = self.config.get('protocol', 'http')
        self.domain = self.config['domain']
        self.token = None
        self.auth_header = None
        self.api_url = '%s://%s.%s/v%s/' % (self.protocol,
                                            self.subdomain,
                                            self.domain,
                                            self.version)
        self.check_session()
        self._create_methods()

    def _build_uri(self, uri, resources, **kwargs):
        final_uri = uri
        for resource in resources:
            final_uri = final_uri.replace('<%s>' % resource, kwargs[resource])

        return final_uri

    def _get_resources_name_from_uri(self, uri):
        resources = re.findall('\<(.*?)\>', uri)
        return resources

    def _set_auth_header(self, token):
        self.auth_header = {'Authorization': 'Token %s' % token}

    def _create_dynamic_method(self, uri, method, aliases, authorization, payload_required):
        if aliases and aliases.get(method):
            func_name = aliases[method]
        else:
            func_name = '%s_%s' % (self.actions_mapping[method], uri)

        if payload_required.get(method, True):
            def _dynamic_method(payload, **kwargs):
                """
                Body for methods that accept a payload.
                """
                resources = self._get_resources_name_from_uri(uri)
                full_uri = self._build_uri(uri, resources, **kwargs)
                full_url = self.api_url + full_uri
                headers = self.json_header if not authorization else {
                    **self.json_header, **self.auth_header}
                full_payload = json.dumps(payload)
                response = getattr(requests, method)(full_url, full_payload, headers=headers)
                return self._return_response(response, uri)
        else:
            def _dynamic_method(**kwargs):
                """
                Body for methods that don't accept a payload.
                """
                resources = self._get_resources_name_from_uri(uri)
                full_uri = self._build_uri(uri, resources, **kwargs)
                full_url = self.api_url + full_uri
                headers = self.json_header if not authorization else {
                    **self.json_header, **self.auth_header}
                response = getattr(requests, method)(full_url, headers=headers)
                return self._return_response(response, uri)

        _dynamic_method.__name__ = func_name
        setattr(self, func_name, _dynamic_method)

    def _create_methods(self):
        for endpoint in self.endpoints:
            uri = endpoint.get('uri')
            methods = endpoint.get('methods')
            aliases = endpoint.get('aliases', None)
            authorization = endpoint.get('authorization')
            payload_required = endpoint.get('payload', {})

            for method in methods:
                self._create_dynamic_method(uri, method, aliases, authorization, payload_required)

    def check_session(self):
        if not self.session_folder.exists():
            os.makedirs(self.path)

        if not self.credentials_file.exists():
            self.credentials_file.touch()
        else:
            token = self.credentials_file.read_text()

            if token:
                self.token = token
                self._set_auth_header(token)

    def _return_response(self, response, uri):
        status_code = response.status_code

        try:
            body = response.json() if response.content else None

            if uri == self.login_uri and status_code == 200:
                self.store_new_token(body['token'])

            elif uri == self.logout_uri and status_code == 204:
                self.delete_token()

            elif uri == self.refresh_token_uri and status_code == 200:
                self.delete_token()
                self.store_new_token(body['token'])

            return body

        except Exception as ex:
            return str(ex)

    def store_new_token(self, token):
        self.credentials_file.write_text(token)
        self.token = token
        self._set_auth_header(token)

    def delete_token(self):
        self.credentials_file.write_text('')
        self.token = None
        self._set_auth_header(None)

    def refresh_token(self):
        headers = {**self.json_header, **self.auth_header}
        response = getattr(requests, 'post')(
            self.api_url + 'refresh_token', headers=headers)
        return self._return_response(response, 'refresh_token')
