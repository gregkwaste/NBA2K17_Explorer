type_dict = {0x44445320: 'DDS',
             0xF07F68CA: 'MODEL',
             0x7EA1CFBB: 'OGG',
             0x305098F0: 'CDF',
             0x94EF3BFF: 'IFF',
             0x504B0304: 'ZIP',
             0x5A4C4942: 'ZLIB'}

archiveName_list = ['0A', '0B', '0C', '0D', '0E', '0F', '0G', '0H', '0I', '0J', '0K', '0L', '0M', '0N', '0O', '0P', '0Q', '0R', '0S', '0T', '0U', '0V', '0W', '0X', '0Y', '0Z',
                    '1A', '1B', '1C', '1D', '1E', '1F', '1G', '1H', '1I', '1J', '1K', '1L', '1M', '1N', '1O', '1P', '1Q', '1R', '1S', '1T', '1U', '1V', '1W', '1X', '1Y', '1Z',
                    '2A', '2B', '2C', '2D', '2E', '2F', '2G', '2H', '2I', '2J', '2K', '2L', '2M', '2N', '2O', '2P', '2Q', '2R', '2S', '2T', '2U', '2V', '2W', '2X', '2Y', '2Z',
                    '3A', '3B', '3C', '3D', '3E', '3F', '3G', '3H']

archiveName_discr = [' - Various 1', ' - PAD' , ' - Various 2', ' - PAD' , ' - Various 3',   ' - PAD' , ' - Various 4',   ' - PAD' , ' - Shoes 1' , ' - PAD' , ' - Classic/Euro',       ' - PAD' ,
                     ' - Sixers',    ' - PAD' , ' - Bucks',     ' - PAD' , ' - Bulls',       ' - PAD' , ' - Cavaliers',   ' - PAD' , ' - Celtics' , ' - PAD' , ' - Clippers',           ' - PAD' ,
                     ' - Grizzlies', ' - PAD' , ' - Hawks',     ' - PAD' , ' - Heat',        ' - PAD' , ' - Hornets',     ' - PAD' , ' - Jazz'    , ' - PAD' , ' - Kings',              ' - PAD' ,
                     ' - Knicks',    ' - PAD' , ' - Lakers',    ' - PAD' , ' - Magic',       ' - PAD' , ' - Mavericks',   ' - PAD' , ' - Nets'    , ' - PAD' , ' - Nuggets',            ' - PAD' ,
                     ' - Pacers',    ' - PAD' , ' - Pelicans',  ' - PAD' , ' - Pistons',     ' - PAD' , ' - Raptors',     ' - PAD' , ' - Rockets' , ' - PAD' , ' - Spurs',              ' - PAD',
                     ' - Suns',      ' - PAD' , ' - Thunder',   ' - PAD' , ' - Timberwolves',' - PAD' , ' - Trailblazers',' - PAD' , ' - Warriors', ' - PAD' , ' - Wizards',            ' - PAD',
                     ' - MyCareer',  ' - PAD' , ' - Various 5', ' - PAD' , ' - Various 6'   ,' - PAD' , ' - Shoes 2'     ,' - PAD' , ' - Various 7',' - PAD',  ' - English Commentary', ' - PAD',
                     ' - Spanish Commentary', ' - PAD',]

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
version = '0.50'
game_title = 'NBA 2K17'

if __name__=='__main__':
    print len(archiveName_list),len(archiveName_discr)