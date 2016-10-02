type_dict = {0x44445320: 'DDS',
             0xF07F68CA: 'MODEL',
             0x7EA1CFBB: 'OGG',
             0x305098F0: 'CDF',
             0x94EF3BFF: 'IFF',
             0x504B0304: 'ZIP',
             0x5A4C4942: 'ZLIB'}

archiveName_list = ['0A', '0B', '0C', '0D', '0E', '0F', '0G', '0H', '0I', '0J', '0K', '0L', '0M', '0N', '0O', '0P', '0Q', '0R', '0S', '0T', '0U', '0V', '0W', '0X', '0Y', '0Z',
                    '1A', '1B', '1C', '1D', '1E', '1F', '1G', '1H', '1I', '1J', '1K', '1L', '1M', '1N', '1O', '1P', '1Q', '1R', '1S', '1T', '1U', '1V', '1W', '1X', '1Y', '1Z',
                    '2A', '2B', '2C', '2D', '2E', '2F', '2G', '2H', '2I', '2J', '2K', '2L', '2M', '2N', '2O', '2P', '2Q', '2R', '2S', '2T', '2U', '2V', '2W', '2X', '2Y', '2Z']

archiveName_discr = [' - Various 1', ' - Various 2', ' - Retro, Euro, College 1', ' - Retro, Euro, College 2', ' - Sixers', ' - Bucks', ' - Bulls', ' - Cavaliers', ' - Celtics', ' - Clippers', ' - Grizzlies', ' - Hawk', ' - Heat',
                     ' - Hornets', ' - Jazz', ' - Kings', ' - Knicks', ' - Lakers', ' - Magic', ' - Mavericks', ' - Nets', ' - Nuggets', ' - Pacers', ' - Pelicans', ' - Pistons', ' - Raptors', ' - Rockets', ' - Spurs',
                     ' - Suns', ' - Thunder', ' - Timberwolves', ' - Trailblazers', ' - Warriors', ' - Wizards', ' - MyCareer', ' - Cheerleader Anims.', ' - Clothing', ' - Shoes', ' - Various Audio 1', ' - Various Audio 2', ' - Various Audio 3', 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ' - Unknown', 0, 0, 0, 0, 0, 0, ' - Animation Fixes']

#for i in range(len(archiveName_list)): archiveName_list[i]+=archiveName_discr[i]

archiveOffsets_list = []
archiveName_dict = {}
settings_dict = {}
bool_dict = {'False': False,
             'True': True}
for i in range(len(archiveName_list)):
    archiveName_dict[archiveName_list[i]] = i
for i in range(len(archiveName_list)):
    settings_dict[archiveName_list[i]] = "False"

index_table = [0x63000000, 0x6E000000, 0x73000000, 0x74000000, 0x70000000]

zip_types = {0xE: 'LZMA', 0: 'NONE', 0x8: 'ZLIB'}
version = '0.40'
