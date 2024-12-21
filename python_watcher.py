import time as t, json as j, os
from watchdog.observers import Observer as O
from watchdog.events import FileSystemEventHandler as F

class ObserverHandler(F):
    def __init__(self, log_file):
        self.log_file = log_file
        self.last_changes = {}

    def on_any_event(self, event):
        dosya_adi = os.path.basename(event.src_path)

        if dosya_adi.startswith(".") or dosya_adi.endswith(("~", "#")):
            return

        if event.event_type == "created":
            degisiklik_turu = "created"
        elif event.event_type == "deleted":
            degisiklik_turu = "deleted"
        elif event.event_type == "modified":
            degisiklik_turu = "modified"
        elif event.event_type == "moved":
            degisiklik_turu = "moved"
        elif event.event_type == "opened":
            degisiklik_turu = "opened"
        else:
            return

        zaman = t.time()
        if dosya_adi in self.last_changes and (zaman - self.last_changes[dosya_adi]) < 1:
            return
        
        zaman_str = t.strftime("%Y-%m-%d %H:%M:%S", t.localtime(zaman))

        log_kaydi = {
            "dosya_adi": dosya_adi,
            "degisiklik_turu": degisiklik_turu,
            "zaman": zaman_str
        }

        try:
            with open(self.log_file, "a") as f:
                j.dump(log_kaydi, f, ensure_ascii=False)
                f.write("\n")
            self.last_changes[dosya_adi] = zaman
        except Exception as e:
            print(f"Log yaz\u0131lamad\u0131: {e}")

if __name__ == "__main__":
    watch_directory = "/home/kali/Desktop/bsm/test"
    log_file = "/home/kali/Desktop/bsm/logs/changes.json"

    pid_file = "/tmp/watcher.pid"
    if os.path.exists(pid_file):
        print("Script zaten \u00e7al\u0131\u015f\u0131yor.")
        exit()
    with open(pid_file, "w") as f:
        f.write(str(os.getpid()))

    event_handler = ObserverHandler(log_file)
    observer = O()
    observer.schedule(event_handler, watch_directory, recursive=True)

    print(f"\u0130zleme ba\u015flad\u0131: {watch_directory}")
    try:
        observer.start()
        while True:
            t.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    finally:
        os.remove(pid_file)
    observer.join()
