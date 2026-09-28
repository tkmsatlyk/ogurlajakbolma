import time
import collector
import link_checker

while True:
    collector.collect()
    link_checker.run_once()
    time.sleep(link_checker.INTERVAL)
