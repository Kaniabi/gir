from __future__ import unicode_literals



#---------------------------------------------------------------------------------------------------
# Entry Point
#---------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    from gir import GetConfig, app
    port = int(GetConfig('FLASK_PORT'))
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=True)
