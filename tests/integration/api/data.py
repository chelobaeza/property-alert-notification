test_post_reference_validation_error_data = (
    {
        "new_preference": {
            "email_enabled": True,
            "sms_enabled": "not a boolean",
        },
        "expected_error": {'detail': [{'type': 'bool_parsing', 'loc': ['body', 'sms_enabled'], 'msg': 'Input should be a valid boolean, unable to interpret input', 'input': 'not a boolean'}]}
    },
    {
        "new_preference": {
            "email_enabled": True,
        },
        "expected_error": {'detail': [{'input': {'email_enabled': True}, 'loc': ['body', 'sms_enabled'], 'msg': 'Field required', 'type': 'missing'}]}
    },
    {
        "new_preference": {
            "sms_enabled": False,
        },
        "expected_error": {'detail': [{'input': {'sms_enabled': False}, 'loc': ['body', 'email_enabled'], 'msg': 'Field required', 'type': 'missing'}]}
    },
)

test_post_notification_validation_error = (
    {
        "new_notification": {
            "message": "Notification message",
            "user_id": 1234
        },
        "expected_error": {}
    },
    {
        "new_notification": {
            "title": "Notification title",
            "user_id": 1234
        },
        "expected_error": {}
    },
    {
        "new_notification": {
            "title": "Notification title",
            "message": "Notification message",
        },
        "expected_error": {}
    },
)