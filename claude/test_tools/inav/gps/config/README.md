# GPS Configuration

GPS-specific configuration script.

## Script

### configure_sitl_gps.py
**Configure GPS provider and settings**

```bash
python3 configure_sitl_gps.py [--port 5760]
```

Sets GPS provider (UBLOX, MSP, NMEA, etc.) and GPS-related settings.

## Related Configuration

**SITL/FC Configuration:** See `../../sitl/` for general SITL and FC configuration scripts:
- `configure_sitl_for_arming.py` - MSP receiver + ARM setup
- `arm_fc_physical.py` - Arm physical FC
- `configure_fc_msp_rx.py` - MSP RX configuration
- And more...

**Blackbox Configuration:** See `../../blackbox/config/` for blackbox logging setup:
- `configure_sitl_blackbox_file.py` - FILE logging
- `configure_sitl_blackbox_serial.py` - SERIAL logging
- `enable_blackbox_feature.py` - Enable BLACKBOX feature flag
- And more...

## See Also

- `../injection/` - GPS data injection (requires GPS provider = MSP)
- `../../sitl/` - General SITL configuration tools
- `../../blackbox/` - Blackbox logging tools
