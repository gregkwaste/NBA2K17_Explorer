import logging
logging.basicConfig(level=logging.INFO)


class SchedulerEntry:

    def __init__(self):
        self.name = None
        self.oldDecompSize = None
        self.newDecompSize = None
        self.oldCompSize = None
        self.newCompSize = None
        self.type = None
        self.localOffset = None
        self.newData = None
        self.oldData = None
        self.archName = None
        self.oaId = None


def scheduler_add_texture(self, im, fileName):
    # Get current selected file
    selmod = self.treeView_3.selectionModel().selectedIndexes()[0].row()
    name, off, oldCompSize, type = self.subfile.files[selmod]

    # Get archive Data
    parent_selmod = self.current_tableView.selectionModel(
    ).selectedIndexes()
    arch_name = self.archiveTabs.tabText(self.archiveTabs.currentIndex())
    subarch_name = self.current_sortmodel.data(
        parent_selmod[0], Qt.DisplayRole)
    subarch_offset = self.current_sortmodel.data(
        parent_selmod[1], Qt.DisplayRole)
    subarch_size = self.current_sortmodel.data(
        parent_selmod[3], Qt.DisplayRole)
    logging.info(arch_name, subarch_offset, subarch_size)

    # Get Subfile Data
    parent_selmod = self.treeView_2.selectionModel().selectedIndexes()
    subfile_name = self.file_list.data(
        parent_selmod[0], Qt.DisplayRole)  # file name
    subfile_off = self.file_list.data(
        parent_selmod[1], Qt.DisplayRole)  # file offset
    subfile_type = self.file_list.data(
        parent_selmod[2], Qt.DisplayRole)  # file type
    subfile_size = self.file_list.data(
        parent_selmod[3], Qt.DisplayRole)  # file size
    # file index
    subfile_index = self.treeView_2.selectionModel().selectedIndexes()[
        0].row()
    chksm = 0

    if subfile_type == 'GZIP LZMA':  # override size for GZIP LZMA
        oldCompSize = subfile_size
        compOffset = 14

    logging.info('Replacing File ', name, 'Size ', oldCompSize)
    t = self.subfile._get_file(selmod)

    if subfile_type == 'ZIP':
        local_off = off
        compOffset = 4
    else:
        local_off = 0

    compFlag = False  # flag for identifying dds files
    if not 'dds' in fileName:
        compFlag = True

    if 'dds' in name:
        # Getting Rest Image Data
        originalImage = dds_file(True, t)
        restDataLen = originalImage._get_rest_size()
        originalImage.data.seek(-restDataLen, 2)
        restData = originalImage.data.read()

        # Calculating Old Image Size
        oldDecompSize = originalImage._get_full_size() + restDataLen

    # Calculating New Image Size

    # Calling the Texture Importer panel
    # if not isinstance(im,dds_file):
    res = ImportPanel()
    res.exec_()

    if res.ImportStatus:  # User has pressed the Import Button
        # Compress the Texture
        comp = res.CurrentImageType
        nmips = res.CurrentMipmap

        # logging.info(originalImage.header.dwMipMapCount,nmips)
        if compFlag:
            logging.info('Converting Texture file')
            self.statusBar.showMessage('Compressing Image...')
            status = call(['./nvidia_tools/nvdxt.exe', '-file', str(fileName),
                           comp, '-nmips', nmips, '-quality_production', '-output', 'temp.dds'])
            f = open('temp.dds', 'rb')
        else:
            # working on an existing dds file
            f = open(fileName, "rb")

        # writing temp.dds to an IO buffer, and fixing the dds header
        t = StringIO()
        t.write(f.read(11))

        if res.swizzleFlag:
            t.write(struct.pack('B', 128))  # writing flag for swizzled dds
            f.read(1)
        else:
            t.write(f.read(1))

        t.write(f.read(16))

        # Overriding Mipmap count when compressing image
        if compFlag:
            t.write(struct.pack('B', int(nmips)))  # writing mipmaps
            f.read(1)
        else:
            t.write(f.read(1))

        t.write(f.read())
        f.close()
        t.seek(0)
        res.destroy()
    else:
        res.destroy()
        self.statusBar.showMessage('Import Canceled')
        return

    #f = open('testing.dds', 'wb')
    # f.write(t.read())
    # f.close()
    t.seek(0)

    f = dds_file(True, t)
    if res.swizzleFlag:
        logging.info('Swizzling Texture')
        f.swizzle_2k()
    t = f.write_texture()

    newData = t.read()

    newData += restData
    newDataSize = len(newData)
    chksm = zlib.crc32(newData) & 0xFFFFFFFF  # calculate Checksum

    k = pylzma.compress(newData, 24)  # use 16777216 bits dictionary
    k = k + k[0:len(k) // 4]  # inflating file
    #comp_f = open('test.dat', 'wb')
    # comp_f.write(k)
    # comp_f.close()
    newCompSize = len(k)

    diff = newCompSize + compOffset - oldCompSize

    logging.info('OldDecompSize: ', oldDecompSize, 'NewDecompSize: ', newDataSize)
    logging.info('OldCompSize: ', oldCompSize,
                 'NewCompSize: ', newCompSize, 'Diff: ', diff)

    # Calculate New Image Size

    # Add item to the scheduler
    if not self.scheduler_model:
        self.scheduler_model = TreeModel(("Name", "ID", "Archive", "Subarchive Name", "Subarchive Offset", "Subarchive Size", "Subfile Index", "Subfile Name", "Subfile Offset", "Subfile Type",
                                          "Subfile Size", "Local File Offset", "Old Decompressed Size", "New Decompressed Size", "Old Compressed Size", "New Compressed Size", "CheckSum", "Diff"))

    gc.collect()
    parent = self.scheduler_model.rootItem
    item = TreeItem((name, selmod, arch_name, subarch_name, subarch_offset, subarch_size, subfile_index, subfile_name, subfile_off,
                     subfile_type, subfile_size, local_off, oldDecompSize, newDataSize, oldCompSize, newCompSize, chksm, diff), parent)
    parent.appendChild(item)
    self.scheduler.setModel(self.scheduler_model)
    self.schedulerFiles.append(k)
    self.statusBar.showMessage('Texture Added to Import Schedule')


def scheduler_add_model(self, tfile):
    # Get current selected file
    selmod = self.treeView_3.selectionModel().selectedIndexes()[0].row()
    name, off, oldCompSize, type = self.subfile.files[selmod]

    # Get archive Data
    parent_selmod = self.current_tableView.selectionModel(
    ).selectedIndexes()
    arch_name = self.archiveTabs.tabText(self.archiveTabs.currentIndex())
    subarch_name = self.current_sortmodel.data(
        parent_selmod[0], Qt.DisplayRole)
    subarch_offset = self.current_sortmodel.data(
        parent_selmod[1], Qt.DisplayRole)
    subarch_size = self.current_sortmodel.data(
        parent_selmod[3], Qt.DisplayRole)
    logging.info(arch_name, subarch_offset, subarch_size)

    # Get Subfile Data
    parent_selmod = self.treeView_2.selectionModel().selectedIndexes()
    subfile_name = self.file_list.data(
        parent_selmod[0], Qt.DisplayRole)  # file name
    subfile_off = self.file_list.data(
        parent_selmod[1], Qt.DisplayRole)  # file offset
    subfile_type = self.file_list.data(
        parent_selmod[2], Qt.DisplayRole)  # file type
    subfile_size = self.file_list.data(
        parent_selmod[3], Qt.DisplayRole)  # file size
    # file index
    subfile_index = self.treeView_2.selectionModel().selectedIndexes()[
        0].row()
    chksm = 0

    if subfile_type == 'GZIP LZMA':  # override size for GZIP LZMA
        oldCompSize = subfile_size
        compOffset = 14

    logging.info('Replacing File ', name, 'Size ', oldCompSize)

    if subfile_type == 'ZIP':
        local_off = off
        compOffset = 4
    else:
        local_off = 0

    tfile.seek(0)
    newData = tfile.read()
    tfile.close()
    newDataSize = len(newData)
    chksm = zlib.crc32(newData) & 0xFFFFFFFF  # calculate Checksum

    # use 16777216 bits dictionary
    k = pylzma.compress(newData, dictionary=24, eos=0)
    k += b'\x00'
    # k=k+k[0:len(k)//4] #inflating file
    #comp_f = open('test.dat', 'wb')
    # comp_f.write(k)
    # comp_f.close()
    newCompSize = len(k)

    diff = newCompSize + compOffset - oldCompSize

    logging.info('OldDecompSize: ', subfile_size, 'NewDecompSize: ', newDataSize)
    logging.info('OldCompSize: ', oldCompSize,
                 'NewCompSize: ', newCompSize, 'Diff: ', diff)

    # Add model to Scheduler
    sched = SchedulerEntry()

    sched.name = name
    sched.selmod = selmod
    sched.arch_name = arch_name

    sched.subarch_name = subarch_name
    sched.subarch_offset = subarch_offset
    sched.subarch_size = subarch_size

    sched.subfile_name = subfile_name
    sched.subfile_off = subfile_off
    sched.subfile_type = subfile_type
    sched.subfile_index = subfile_index
    sched.subfile_size = subfile_size

    sched.local_off = local_off
    sched.oldCompSize = oldCompSize
    sched.oldDecompSize = subfile_size
    sched.newCompSize = newCompSize
    sched.newDataSize = newDataSize
    sched.chksm = chksm
    sched.diff = diff

    self.addToScheduler(sched, k)  # Add to Scheduler
    self.statusBar.showMessage('Model Added to Import Scheduler')
