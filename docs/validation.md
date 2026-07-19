# DG1022 Validation

Validation date: 2026-07-19

## Instrument

```text
RIGOL TECHNOLOGIES,DG1022,DG1D124605159,00.02.00.06.00.02.07
/dev/usbtmc3
```

The physical connection was DG CH1 to DS1152E CH1 and DG CH2 to DS1152E CH2.

## Catalog And Transport

- 21/21 programming-guide subsystems represented
- 106 merged catalog entries
- 214 operations after expanding channel and query/write variants
- 98 live query instances audited; 95 returned directly
- Empty nonvolatile catalog and unnamed memory-slot responses account for two
  device-state-dependent cases
- CH2 pulse duty required `PULSe:DCYC:CH2`; that rendering is modeled explicitly

Original-value query-set writeback produced 66 direct passes from 82 instances.
The other 16 were internal parameters of disabled AM/FM/PM/FSK/sweep/burst modes.
After enabling each owning mode, all six mode families wrote and read back correctly.

The transport omits `USBTMC_IOCTL_EOM_ENABLE`, which makes this instrument time
out. It uses 2 ms query delay and 100 ms ordinary command delay. High-level phase
configuration adds a device-specific settling interval before `PHASe:ALIGN`.

## Functional Checks

- APPLy sine/square/ramp/pulse/noise/DC/user: 7 waveforms x 2 channels passed
- AM/FM/PM/FSK, linear sweep, and 5-cycle burst observed on the DS1152E
- Counter enable/query/disable passed
- Display, clock, language, remote/lock/local, memory slots, phase align, channel
  copy, and coupling register operations passed
- Arbitrary data lifecycle passed: upload, VOLATILE, 4096-point expansion, copy,
  catalog/free-space, rename, download, and delete
- Repeated arbitrary BIN/CSV/JSON download passed using the three-command
  `DATA:LOAD` state machine
- CH1-to-CH2 copy preserved ramp, 1234 Hz, 1.5 Vpp, 0.2 V offset, and 30 degree
  phase settings

Cross-channel phase must be measured from the scope's 8192-point `MAXIMUM` record.
The 600-point `NORMAL` transfers are not reliably aligned between channels. The
high-level phase path measured 60.4 degrees for a 60 degree command; separate 30
and 90 degree checks measured approximately 30.6 and 89.5 degrees.

Channel coupling parameters read and write correctly, but later SCPI frequency
writes do not dynamically move the other channel on this instrument. Coupling is
not claimed as a software frequency tracker.

## Representative Measurements

```text
Square duty: CH1 25% -> 24.8%, CH2 75% -> 75.0%
Pulse duty:  CH1 20% -> 20.0%, CH2 60% -> 60.3%
DC level:    +0.5 V -> +0.496 V, -0.5 V -> -0.521 V
FM:          about 7.6 to 12.2 kHz for 10 kHz +/- 2 kHz
FSK:         about 5.0 kHz and 10.0 kHz clusters
Burst:       five positive-going crossings per complete burst
Sweep:       repeating 200 Hz to 2 kHz linear sweep over 0.1 s
```

At 2 Vpp carrier and 50% AM depth, this instrument produced an overall envelope
of about 1.50 Vpp. This is recorded as instrument behavior rather than corrected
in software.

## Final Connected Baseline

```text
CH1: sine, 1 kHz, 2 Vpp, 0 V offset, output ON, load INF
CH2: sine, 2 kHz, 2 Vpp, 0 V offset, output ON, load INF
AM/FM/PM/FSK/sweep/burst/coupling: OFF
DS measurement CH1: 1.000 kHz, 2.04 Vpp
DS measurement CH2: 1.980 kHz, 2.02 Vpp
```

Unit test result: 13 passed.
