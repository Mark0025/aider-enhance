WORKFLOW_TEMPLATES = {
    "python_development": {
        "name": "Python Development",
        "model": "gpt-4-turbo",
        "settings": {
            "auto_lint": True,
            "test_cmd": "pytest",
            "git_integration": True
        }
    },
    "web_development": {
        "name": "Web Development",
        "model": "claude-3-sonnet",
        "settings": {
            "file_watchers": True,
            "hot_reload": True
        }
    }
}
