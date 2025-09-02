<?php
$metadata['__DYNAMIC:1__'] = [
    'host' => '__DEFAULT__',

    'auth' => 'example-userpass',

    'privatekey' => 'idp.pem',
    'certificate' => 'idp.crt',

    'authproc' => [
        3 => [
            'class' => 'saml:AttributeNameID',
            'attribute' => 'username',
            'Format' => 'urn:oasis:names:tc:SAML:2.0:nameid-format:persistent',
        ],
    ],

    'NameIDFormat' => 'urn:oasis:names:tc:SAML:2.0:nameid-format:persistent',
];
