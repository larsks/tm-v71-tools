# Memory Map

| Address         | Description                                       |
|-----------------|---------------------------------------------------|
| 0x17            | Key lock (0=disabled, 1=enabled)                  |
| 0x21            | PC port speed (0=9600, 1=19200, 2=38400, 3=57600) |
| 0x170           | Repeated ID (12 characters)                       |
| 0x201           | Band A memory/vfo mode (0=vf0, 1=memory)          |
| 0x202           | Band A selected frequency band                    |
| 0x20D           | Band B memory/vfo mode                            |
| 0x20E           | Band B selected frequency band                    |
| 0x2e0           | Poweron message                                   |
| 0x231           | PTT band                                          |
| 0x232           | Control band                                      |
| 0x250           | Band A vfo setting (8 bytes)                      |
| 0x2C0           | Band B vfo setting                                |
| 0x1700 - 0x557F | Channel memory (16 bytes * 1000)                  |
| 0x5800 - 0x773f | Channel names (8 bytes * 1000)                    |
| 0x77e0 - 0x782D | WX channel names                                  |
| 0x7d00 - 0x7d9f | Group names (16 bytes * 8 groups)                 |
| 0x7da0          | Program memory names (16 bytes * 5 PMs)           |
