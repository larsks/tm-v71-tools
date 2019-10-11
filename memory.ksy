---
meta:
  id: memory
  title: "TMV71 Channels"
  license: GPL-3.0-or-later
  ks-version: 0.8
  endian: le

instances:
  tables:
    type: tables

  dtmf_codes:
    pos: 0x30
    type: str
    encoding: ascii
    terminator: 0xff
    size: 16
    repeat: expr
    repeat-expr: 10

  dtmf_names:
    pos: 0xd0
    type: str
    encoding: ascii
    terminator: 0xff
    size: 8
    repeat: expr
    repeat-expr: 10

  echolink_names:
    pos: 0x120
    type: str
    encoding: ascii
    terminator: 0xff
    size: 8
    repeat: expr
    repeat-expr: 10

  echolink_codes:
    pos: 0x190
    type: str
    encoding: ascii
    terminator: 0xff
    size: 8
    repeat: expr
    repeat-expr: 10

  program_memory:
    pos: 0x200
    size: 512
    type: program_memory
    repeat: expr
    repeat-expr: 6

  channel_extended_flags:
    pos: 0xe00
    type: channel_extended_flags
    repeat: expr
    repeat-expr: 1000

  channels:
    pos: 0x1700
    type: channel(_index)
    repeat: expr
    repeat-expr: 1000

  program_scan_memory:
    pos: 0x5580
    type: program_scan_memory
    repeat: expr
    repeat-expr: 10

  # Names in the tm-v71a are padded with `0xff` bytes up to their
  # maxium length. By specifying both `size` and `terminator` we
  # consume the correct number of bytes and return a string that
  # does not contain the padding bytes.
  channel_names:
    pos: 0x5800
    type: str
    encoding: ascii
    terminator: 0xff
    size: 8
    repeat: expr
    repeat-expr: 1000

  wx_channel_names:
    pos: 0x77e0
    type: str
    encoding: ascii
    terminator: 0xff
    size: 8
    repeat: expr
    repeat-expr: 10

  group_names:
    pos: 0x7d00
    type: str
    encoding: ascii
    terminator: 0xff
    size: 16
    repeat: expr
    repeat-expr: 8

  program_memory_names:
    pos: 0x7da0
    type: str
    encoding: ascii
    terminator: 0xff
    size: 16
    repeat: expr
    repeat-expr: 5

types:
  tables:
    doc: |
      This is a value-only collection of tables used to map
      numeric constants in the channel data into actual values.
    instances:
      step_size:
        value: >-
          [5, 6.25, 28.33, 10, 12.5, 15, 20, 25, 30, 50, 100]
      tone_frequency:
        value: >-
          [67, 69.3, 71.9, 74.4, 77, 79.7, 82.5, 85.4, 88.5, 91.5,
          94.8, 97.4, 100, 103.5, 107.2, 110.9, 114.8, 118.8, 123,
          127.3, 131.8, 136.5, 141.3, 146.2, 151.4, 156.7, 162.2,
          167.9, 173.8, 179.9, 186.2, 192.8, 203.5, 240.7, 210.7,
          218.1, 225.7, 229.1, 233.6, 241.8, 250.3, 254.1]
      dcs_code:
        value: >-
          [23, 25, 26, 31, 32, 36, 43, 47, 51, 53, 54, 65, 71, 72, 73,
           74, 114, 115, 116, 122, 125, 131, 132, 134, 143, 145, 152,
           155, 156, 162, 165, 172, 174, 205, 212, 223, 225, 226, 243,
           244, 245, 246, 251, 252, 255, 261, 263, 265, 266, 271, 274,
           306, 311, 315, 325, 331, 332, 343, 346, 351, 356, 364, 365,
           371, 411, 412, 413, 423, 431, 432, 445, 446, 452, 454, 455,
           462, 464, 465, 466, 503, 506, 516, 523, 565, 532, 546, 565,
           606, 612, 624, 627, 631, 632, 654, 662, 664, 703, 712, 723,
           731, 732, 734, 743, 754]
  common_vfo_fields:
    seq:
      - id: rx_freq_raw
        type: u4
      - id: rx_step_raw
        type: u1
      - id: mod
        type: u1
        enum: modulation
      - id: flags
        type: channel_flags
      - id: tone_frequency_raw
        type: u1
      - id: ctcss_frequency_raw
        type: u1
      - id: dcs_code_raw
        type: u1
      - id: tx_offset_raw
        type: u4
      - id: tx_step_raw
        type: u1
      - id: padding
        type: u1
    instances:
      deleted:
        value: true
        if: rx_freq_raw == 0xFFFFFFFF
      rx_freq:
        value: rx_freq_raw / 1000000.0
      rx_step:
        value: _root.tables.step_size[rx_step_raw]
      tone_freq:
        value: _root.tables.tone_frequency[tone_frequency_raw]
      ctcss_freq:
        value: _root.tables.tone_frequency[ctcss_frequency_raw]
      dcs_code:
        value: _root.tables.dcs_code[dcs_code_raw]
      tx_offset:
        value: tx_offset_raw / 1000000.0
      tx_step:
        value: "tx_step_raw == 0xff ? 0 : tx_step_raw"
  channel:
    params:
      - id: number
        type: u2
    seq:
      - id: common
        type: common_vfo_fields
  program_scan_memory:
    seq:
      - id: lower
        type: common_vfo_fields
      - id: upper
        type: common_vfo_fields
  vfo_config:
    seq:
      - id: common
        type: common_vfo_fields
  channel_flags:
    doc: |
      These flags are included in byte 6 of the channel entry.
    seq:
      - id: unknown
        type: b1
      - id: admit
        type: b3
        enum: admit
      - id: reverse
        type: b1
      - id: split
        type: b1
      - id: shift
        type: b2
        enum: shift_direction
  extended_flag_bits:
    seq:
      - id: unknown
        type: b7
      - id: lockout
        type: b1
  channel_extended_flags:
    seq:
      - id: band
        type: u1
      - id: flags
        type: extended_flag_bits
  program_memory:
    instances:
      band_a_mode:
        pos: 0x01
        type: u1
      band_a_freq_band:
        pos: 0x02
        type: u1
        enum: freq_band
      band_a_power:
        pos: 0x07
        type: u1
        enum: tx_power
      band_b_mode:
        pos: 0x0D
        type: u1
      band_b_freq_band:
        pos: 0x0E
        type: u1
        enum: freq_band
      band_b_power:
        pos: 0x13
        type: u1
        enum: tx_power
      s_meter_squelch:
        pos: 0x15
        type: u1
      current_menu_item:
        pos: 0x15
        type: u1
      ptt_band:
        pos: 0x32
        type: u1
      ctrl_band:
        pos: 0x33
        type: u1
      poweron_message:
        pos: 0xE0
        type: str
        encoding: ascii
        terminator: 0xff
        size: 12
      group_link:
        pos: 0xF0
        type: str
        encoding: ascii
        terminator: 0xff
        size: 10
      beep:
        pos: 0x150
        type: u1
      beep_volume:
        pos: 0x151
        type: u1
      band_mask_a:
        pos: 0x180
        type: u1
        repeat: expr
        repeat-expr: 5
      band_mask_b:
        pos: 0x185
        type: u1
        repeat: expr
        repeat-expr: 5
      vfo_settings_a:
        pos: 0x40
        type: common_vfo_fields
        repeat: expr
        repeat-expr: 5
      vfo_settings_b:
        pos: 0x90
        type: common_vfo_fields
        repeat: expr
        repeat-expr: 5
enums:
  channel_band:
    5: vhf
    8: uhf
  shift_direction:
    0: simplex
    1: up
    2: down
    3: invalid
  modulation:
    0: fm
    1: am
    2: nfm
    0xff: invalid
  admit:
    0: none
    4: tone
    2: ctcss
    1: dcs
    7: invalid
  freq_band:
    0: band_118
    1: band_144
    2: band_220
    3: band_300
    5: band_430
    6: band_1200
  tx_power:
    0: high
    1: medium
    2: low
