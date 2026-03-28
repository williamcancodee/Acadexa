"""Compatibility launcher.

`main_fixed.py` is the canonical application entrypoint.
This file is kept for backward compatibility so `python main_db.py` still works.
"""

import os

from main_fixed import app, db


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
