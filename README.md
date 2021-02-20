# T660305R CO2 sensor notes/experiments

Rough "lab notebook" while testing and using some older CO2 modules whose official documentation appears to have begun bit-rotting.

## General notes/links

Looks like these sensors were branded as GE Sensing Safeaire T6603-5 although made by Telaire even at the time. Amphenol may have bought Telaire since then.

The best guide left on the web might be: <https://ecorenovator.org/forum/showthread.php?t=3600>

There's an Arduino library here: <https://github.com/LuisM78/T6603>

And some discussion: <https://picaxeforum.co.uk/threads/co2-sensor-help.25942/>


The best PDF I can find is unfortunately not available from an original source:
<https://file.yzimgs[.]com/321940/2012082417090077.pdf>  [may or may not be a trustworthy download site]

There's a different PDF version with a slightly more specific provenance here as well:
<https://web.archive.org/web/20160416212536/http://www.sensorexpert.com.cn/UploadFiles/Others/20120910142843_18796.pdf>

This may also be one of the original manuals although it has a different product number: <https://web.archive.org/web/20101117090509/http://www.ge-mcs.com/download/sensing-manuals/T63182-003.pdf>

The most relevant bits I see in those basic overviews are that the pins in the white plastic header should be (L-to-R, with the gold part on top and the header at the bottom):

* 1 — UART RX
* 2 — UART TX
* 3 — V+ [power input]
* 4 — V- [power ground]
* 5 — PWM or control signal output

V+ should get 5 volts (±0.5V), peak consumption 150ma.

UART defaults to 19200 baud, no parity, 1 stop bit.

The UART protocol seems to match the currently available documentation <https://www.amphenol-sensors.com/en/literature/561-telaire-co2-sensors-uart-communications-protocol>. Note the product-specific PDFs above mention a more specific "Refer to T6603_UART_Protocol document PD0081" which I've only found at some content farm thing <https://wenku.baidu[.]com/view/b5f899b7a26925c52dc5bf17.html> although possibly available for download to "VIP" users in exchange for email address and/or installing an app and/or giving credit card and/or who knows.

The closest new parts would either be:

* T6613: <https://www.amphenol-sensors.com/en/telaire/co2/525-co2-sensor-modules/321-t6613>
* T6703: <https://www.amphenol-sensors.com/en/telaire/co2/525-co2-sensor-modules/3400-t6703>

It looks like the MH-Z19C might be the current popular "go-to" sensor for hobby CO2 stuff these days.

<https://en.wikipedia.org/w/index.php?title=Carbon_dioxide_sensor&oldid=1000144008> for general background on how CO2 sensors work. The T6603 is presumedly NDIR as it blinks a light inside its chamber thing each time it gives a reading.

## Connecting via a USB TTL dongle

Those USB TTL serial UART adapters are pretty handy for communicating with this, since they provide the +5V needed and of course the serial itself. I guess the color coding isn't maybe always consistent between models but with the dongle I have it's:

* plastic header pin 1 — green
* plastic header pin 2 — white
* plastic header pin 3 — red
* plastic header pin 3 — black


## Sample commands

For initial poking/prodding I started with Serial.app on my macOS, which doesn't have a great way to *read* binary data. What I do is set Raw Bytes in the "Serial > Preferences > Logging" tab, <kbd>⌘L</kbd> to "Terminal > Start Log" and then <kbd>⌘T</kbd> to "Terminal > Send String…" which does support hex stuff.

Here's some handy/useful ones:

```
via T63182-004-091614-web

0xFFFE020203
0xFFFE020203 - CMD_READ GAS_PPM
0xFFFE01B6 - CMD_STATUS
0xFFFE02C000 - CMD_SELF_TEST START
0xFFFE02C001 - CMD_SELF_TEST RESULTS

0xFFFE02020F - CMD_READ ELEVATION
0xFFFE04030F0180 - CMD_UPDATE ELEVATION 384


0xFFFE020211 — CMD_VFY_SGPT_PPM [was 1000]
0xFFFE0403110190 — CMD_SET_SGPT_PPM [to 400]
0xFFFE019B — CMD_SGPT_CALIBRATE

0xFFFE05004D41524B - CMD_LOOPBACK "MARK"

0xFFFE01BD - CMD_STREAM_DATA
```

Then to read the responses I open the log in HexFiend (using "Revert to Saved" to update when necessary…) and find the stuff manually. Definitely not ideal, so once that was working I moved on to the…

## Python files in this repo

For some reason these only work once (?!). That is, if I run them and then Ctrl-C out of them I have to unplug and re-plug the TTL adapter in before they work again. Haven't really taken much time to troubleshoot why.

Anyway, the `log.py` was the first one, has some extra debugging/experimental junk in it and "polls" the device every 5 seconds. Then I realized the sensor can "stream" the data itself so `log_stream.py` uses that instead. You'll need PySerial installed, and then pass the command your serial port, e.g.:

```
python3 -m venv env
. env/bin/activate
pip install -r requirements.txt

./log_stream.py /dev/cu.Repleo-PL2303-00001014
# sensor doesn't output while it warms up, but eventually you should get output like…
2021-02-20T12:10:04,1430
2021-02-20T12:10:10,1446
2021-02-20T12:10:16,1466
2021-02-20T12:10:22,1484
2021-02-20T12:10:27,1570
2021-02-20T12:10:33,1571
2021-02-20T12:10:39,1578
2021-02-20T12:10:45,1575
2021-02-20T12:10:51,1575
2021-02-20T12:10:57,1583
2021-02-20T12:11:03,1586
2021-02-20T12:11:08,1587
2021-02-20T12:11:14,1592
2021-02-20T12:11:20,1597
2021-02-20T12:11:26,1599
2021-02-20T12:11:32,1603
2021-02-20T12:11:38,1609
2021-02-20T12:11:44,1607
```

…which you can open as CSV in Excel or Numbers.app or R or whatever and graph.

…or it might just crash and burn at the slightest provocation, usually because it didn't get any data back from the sensor (instead of the expected 5 bytes). Try turning it off and back on again or ???

## Script buffering issues when logging via tee

It's nice to see the logs AND capture them. You can pipe into `tee` for this e.g. `./log_stream.py /dev/cu.Repleo-PL2303-00001014 | tee -a ~Desktop/co2_log.csv` but that didn't really work "right" by default because pipes introduce a buffer (4096 bytes or so, probably depending on platform) and so you won't see data for a long time. The scripts now workaround this by a Python flag.


    # (doesn't work... some potential explanation in comments and related posts)
    # https://unix.stackexchange.com/questions/25372/turn-off-buffering-in-pipe#comment225838_25378
    brew install coreutils
    # the following does NOT work
    ./log_stream.py /dev/cu.Repleo-PL2303-00001014 | gstdbuf -o0 tee -a ~/Desktop/co2-overnight.csv

    # … passing `-u` to Python *does* work (now in shebang of scripts) via:
    # https://unix.stackexchange.com/questions/25372/turn-off-buffering-in-pipe#comment1037095_53445
