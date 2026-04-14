try:
    from win10toast import ToastNotifier
    toaster = ToastNotifier()
except ImportError:
    toaster = None

def notify(title, msg):
    print(f"NOTIFICATION: {title} - {msg}")
    if toaster:
        try:
            toaster.show_toast(title, msg, duration=5, threaded=True)
        except Exception as e:
            print(f"Toast error: {e}")