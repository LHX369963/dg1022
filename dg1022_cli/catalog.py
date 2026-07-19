from __future__ import annotations

from dataclasses import dataclass

from .errors import ProtocolError


@dataclass(frozen=True)
class CommandSpec:
    name: str
    command: str
    kind: str
    section: str
    parameters: str = ""
    description: str = ""
    value_style: str = "space"

    @property
    def can_query(self) -> bool:
        return self.kind in {"query", "query-set"}

    @property
    def can_write(self) -> bool:
        return self.kind in {"set", "action", "query-set"}


def _s(name: str, command: str, kind: str, section: str, parameters: str = "", *,
       description: str = "", value_style: str = "space") -> CommandSpec:
    return CommandSpec(name, command, kind, section, parameters, description, value_style)


COMMANDS: tuple[CommandSpec, ...] = (
    _s("general.idn", "*IDN", "query", "ieee488", description="Instrument identity"),
    *(_s(f"apply.{name}", f"APPLy:{command}{{ch}}", "set", "apply",
         "[frequency[,amplitude[,offset]]]", description=f"Configure {name} output")
      for name, command in (("sine", "SINusoid"), ("square", "SQUare"), ("ramp", "RAMP"),
                            ("pulse", "PULSe"), ("noise", "NOISe"), ("dc", "DC"), ("user", "USER"))),
    _s("apply.current", "APPLy{ch}", "query", "apply", description="Current waveform configuration"),
    _s("function.waveform", "FUNCtion{ch}", "query-set", "function", "SINusoid|SQUare|RAMP|PULSe|NOISe|DC|USER"),
    _s("function.user", "FUNCtion:USER{ch}", "query-set", "function", "arbitrary waveform name|VOLATILE"),
    _s("function.square-duty", "FUNCtion:SQUare:DCYCle{ch}", "query-set", "function", "percent|MINimum|MAXimum"),
    _s("function.ramp-symmetry", "FUNCtion:RAMP:SYMMetry{ch}", "query-set", "function", "percent|MINimum|MAXimum"),
    _s("frequency.output", "FREQuency{ch}", "query-set", "frequency", "frequency|MINimum|MAXimum"),
    *(_s(f"frequency.{name}", f"FREQuency:{command}", "query-set", "frequency", "frequency|MINimum|MAXimum")
      for name, command in (("start", "STARt"), ("stop", "STOP"), ("center", "CENTer"), ("span", "SPAN"))),
    *(_s(f"voltage.{name}", f"VOLTage{suffix}{{ch}}", "query-set", "voltage", parameters)
      for name, suffix, parameters in (
          ("amplitude", "", "amplitude|MINimum|MAXimum"), ("high", ":HIGH", "voltage|MINimum|MAXimum"),
          ("low", ":LOW", "voltage|MINimum|MAXimum"), ("offset", ":OFFSet", "offset|MINimum|MAXimum"),
          ("unit", ":UNIT", "VPP|VRMS|DBM"))),
    _s("output.enabled", "OUTPut{ch}", "query-set", "output", "OFF|ON"),
    _s("output.load", "OUTPut:LOAD{ch}", "query-set", "output", "ohm|INFinity|MINimum|MAXimum"),
    _s("output.polarity", "OUTPut:POLarity{ch}", "query-set", "output", "NORMal|INVerted"),
    _s("output.sync", "OUTPut:SYNC", "query-set", "output", "OFF|ON"),
    _s("output.trigger-slope", "OUTPut:TRIGger:SLOPe", "query-set", "output", "POSitive|NEGative"),
    _s("output.trigger", "OUTPut:TRIGger", "query-set", "output", "OFF|ON"),
    *(_s(f"pulse.{name}", f"PULSe:{command}{{ch}}", "query-set", "pulse", parameters)
      for name, command, parameters in (("period", "PERiod", "seconds|MINimum|MAXimum"),
                                        ("width", "WIDTh", "seconds|MINimum|MAXimum"),
                                        ("duty", "{pulse_duty}", "percent|MINimum|MAXimum"))),
    *(_s(f"am.{name}", command, "query-set", "am", parameters) for name, command, parameters in (
        ("source", "AM:SOURce", "INTernal|EXTernal"), ("internal-function", "AM:INTernal:FUNCtion", "SIN|SQU|RAMP|NRAM|TRI|NOIS|USER"),
        ("internal-frequency", "AM:INTernal:FREQuency", "frequency|MINimum|MAXimum"),
        ("depth", "AM:DEPTh", "percent|MINimum|MAXimum"), ("enabled", "AM:STATe", "OFF|ON"))),
    *(_s(f"fm.{name}", command, "query-set", "fm", parameters) for name, command, parameters in (
        ("source", "FM:SOURce", "INTernal|EXTernal"), ("internal-function", "FM:INTernal:FUNCtion", "SIN|SQU|RAMP|NRAM|TRI|NOIS|USER"),
        ("internal-frequency", "FM:INTernal:FREQuency", "frequency|MINimum|MAXimum"),
        ("deviation", "FM:DEViation", "frequency|MINimum|MAXimum"), ("enabled", "FM:STATe", "OFF|ON"))),
    *(_s(f"pm.{name}", command, "query-set", "pm", parameters) for name, command, parameters in (
        ("source", "PM:SOURce", "INTernal|EXTernal"), ("internal-function", "PM:INTernal:FUNCtion", "SIN|SQU|RAMP|NRAM|TRI|NOIS|USER"),
        ("internal-frequency", "PM:INTernal:FREQuency", "frequency|MINimum|MAXimum"),
        ("deviation", "PM:DEViation", "degrees|MINimum|MAXimum"), ("enabled", "PM:STATe", "OFF|ON"))),
    *(_s(f"fsk.{name}", command, "query-set", "fsk", parameters) for name, command, parameters in (
        ("source", "FSK:SOURce", "INTernal|EXTernal"), ("frequency", "FSK:FREQuency", "frequency|MINimum|MAXimum"),
        ("rate", "FSK:INTernal:RATE", "rate|MINimum|MAXimum"), ("enabled", "FSK:STATe", "OFF|ON"))),
    *(_s(f"sweep.{name}", command, "query-set", "sweep", parameters) for name, command, parameters in (
        ("spacing", "SWEep:SPACing", "LINear|LOGarithmic"), ("time", "SWEep:TIME", "seconds|MINimum|MAXimum"),
        ("enabled", "SWEep:STATe", "OFF|ON"))),
    *(_s(f"trigger.{name}", command, "query-set", "trigger", parameters) for name, command, parameters in (
        ("source", "TRIGger:SOURce", "IMMediate|EXTernal|BUS"), ("slope", "TRIGger:SLOPe", "POSitive|NEGative"),
        ("delay", "TRIGger:DELay", "seconds|MINimum|MAXimum"))),
    *(_s(f"burst.{name}", command, "query-set", "burst", parameters) for name, command, parameters in (
        ("mode", "BURSt:MODE", "TRIGgered|GATed"), ("cycles", "BURSt:NCYCles", "cycles|INFinity|MINimum|MAXimum"),
        ("period", "BURSt:INTernal:PERiod", "seconds|MINimum|MAXimum"),
        ("phase", "BURSt:PHASe", "degrees|MINimum|MAXimum"), ("enabled", "BURSt:STATe", "OFF|ON"),
        ("gate-polarity", "BURSt:GATE:POLarity", "NORMal|INVerted"))),
    _s("data.values", "DATA", "set", "data", "VOLATILE,value,value,..."),
    _s("data.dac", "DATA:DAC", "set", "data", "VOLATILE,value,value,..."),
    _s("data.copy", "DATA:COPY", "set", "data", "destination[,VOLATILE]"),
    _s("data.delete", "DATA:DELete", "set", "data", "arbitrary waveform name"),
    _s("data.catalog", "DATA:CATalog", "query", "data"),
    _s("data.rename", "DATA:RENAME", "set", "data", "destination,new-name"),
    _s("data.nv-catalog", "DATA:NVOLatile:CATalog", "query", "data"),
    _s("data.nv-free", "DATA:NVOLatile:FREE", "query", "data"),
    _s("data.points", "DATA:ATTRibute:POINts", "query", "data", "arbitrary waveform name"),
    _s("data.load", "DATA:LOAD", "transfer", "data", "optional arbitrary waveform name",
       description="Two-stage device-to-host arbitrary waveform transfer"),
    _s("memory.state-name", "MEMory:STATe:NAME", "query-set", "memory", "slot[,name]"),
    _s("memory.state-delete", "MEMory:STATe:DELete", "set", "memory", "slot 0..10"),
    _s("memory.auto-recall", "MEMory:STATe:RECall:AUTO", "query-set", "memory", "OFF|ON"),
    _s("memory.state-valid", "MEMory:STATe:VALid", "query", "memory", "slot 0..10"),
    _s("memory.state-count", "MEMory:NSTates", "query", "memory"),
    _s("system.error", "SYSTem:ERRor", "query", "system"),
    _s("system.version", "SYSTem:VERSion", "query", "system"),
    _s("system.beeper", "SYSTem:BEEPer:STATe", "query-set", "system", "OFF|ON"),
    _s("system.local", "SYSTem:LOCal", "action", "system"),
    _s("system.remote-lock", "SYSTem:RWLock", "action", "system"),
    _s("system.remote", "SYSTem:REMote", "action", "system"),
    _s("system.clock-source", "SYSTem:CLKSRC", "set", "system", "EXT|INT"),
    _s("system.language", "SYSTem:LANGuage", "set", "system", "CHINESE|ENGLISH"),
    _s("phase.output", "PHASe{ch}", "query-set", "phase", "degrees|MINimum|MAXimum"),
    _s("phase.align", "PHASe:ALIGN", "action", "phase"),
    _s("display.enabled", "DISPlay", "set", "display", "OFF|ON"),
    _s("display.contrast", "DISPlay:CONTRAST", "set", "display", "integer 0..31"),
    _s("display.luminance", "DISPlay:LUMINANCE", "set", "display", "integer 0..31"),
    _s("coupling.enabled", "COUPling", "query-set", "coupling", "OFF|ON"),
    _s("coupling.base-channel", "COUPling:BASEdchannel", "query-set", "coupling", "CH1|CH2", value_style="colon"),
    _s("coupling.phase-deviation", "COUPling:PHASEDEViation", "query-set", "coupling", "degrees -180..180"),
    _s("coupling.frequency-deviation", "COUPling:FREQDEViation", "query-set", "coupling", "0..20 MHz"),
    _s("coupling.channel-copy", "COUPling:CHANNCopy", "set", "coupling", "1>2|2>1"),
    _s("counter.enabled", "COUNter", "set", "counter", "OFF|ON"),
    _s("counter.coupling", "COUNter:COUPling", "query-set", "counter", "AC|DC"),
    _s("counter.sensitivity", "COUNter:SENSitivity", "query-set", "counter", "LOW|MEDIUM|HIGH"),
    _s("counter.trigger-level", "COUNter:TLEVel", "query-set", "counter", "MIN|MAX|0.0..99.9"),
    _s("counter.high-frequency-reject", "COUNter:HFRS", "query-set", "counter", "OFF|ON"),
    *(_s(f"counter.{name}", f"COUNter:{command}", "query", "counter") for name, command in (
        ("frequency", "FREQuency"), ("period", "PERiod"), ("duty", "DCYCle"),
        ("positive-width", "POSWidth"), ("negative-width", "NEGWidth"))),
)


COMMAND_BY_NAME = {item.name: item for item in COMMANDS}


def get_command(name: str) -> CommandSpec:
    try:
        return COMMAND_BY_NAME[name]
    except KeyError as exc:
        raise ProtocolError(f"unknown manual command {name!r}; use 'dg1022 commands list'") from exc


def render_command(spec: CommandSpec, channel: int | None) -> str:
    if "{pulse_duty}" in spec.command:
        if channel not in {1, 2}:
            raise ProtocolError(f"{spec.name} requires --channel 1 or 2")
        return spec.command.format(pulse_duty="DCYCle" if channel == 1 else "DCYC:CH2", ch="")
    if "{ch}" not in spec.command:
        if channel is not None:
            raise ProtocolError(f"{spec.name} does not take --channel")
        return spec.command
    if channel not in {1, 2}:
        raise ProtocolError(f"{spec.name} requires --channel 1 or 2")
    return spec.command.format(ch="" if channel == 1 else ":CH2")
