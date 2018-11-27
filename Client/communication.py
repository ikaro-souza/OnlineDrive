SERVER_ADDRESS = ('localhost', 1001)
BUFFSIZE = 65536

ACTIONS = [
    'LOG',
    'REG',
    'DISCONNECT',
    'UPDATE'
]

RESULTS = {
    'LOG_SUCCESS': 'User logged.',
    'LOG_FAIL': 'User not registered.',
    'REG_SUCCESS': 'User registered.',
    'REG_FAIL': 'User already exists.',
    'FILE_SENT': 'ALl file data sent.',
    'ALL_SENT': 'All files sent.',
    'NO_FILES': 'No files to send.',
    'F_SEND_ERR': 'Failed to send file.'
}
