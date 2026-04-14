from win10toast import ToastNotifier
toaster = ToastNotifier()

def notify(title, msg):
    toaster.show_toast(title, msg, duration=5, threaded=True)