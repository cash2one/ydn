#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import sys
import msgpack
import ad_manager
import mobile_core_ssp

# 批量导入资源到 ad_manager
def import_to_admanager(filename):
    manager = ad_manager.AdManager()
    with open(filename) as f:
        for line in f:
            line = line.strip()
            key, key_type, src, token = line.split("\t")
            src = int(src)
            ad = {'src': src, 'token': token}
            ret = manager.set(key, key_type, ad)
            st = 'SUCCESS'
            if ret is None:
                st = 'FAILURE'
            print >> sys.stderr, "{}\t{}".format(st, line)


# 批量获取 mobile_core 的资源
def get_mobile_core(filename):
    ssp = mobile_core_ssp.MobileCoreSSP(None, None, None, None)
    with open(filename, "w") as f:
        ssp.update(f)


def import_to_mobile_core(filename):
    mobile_core = mobile_core_ssp.MobileCoreSSP(None, None, None, None)
    with open(filename) as f:
        for line in f:
            line = line.strip()
            token, title, desc, icon, i_url, c_url = line.split("\t")
            ad = {
                'url': c_url,
                'description': desc,
                'title': title,
                'rank': None,
                'sitehost': None,
                'imp_url': i_url,
                'icon': icon,
            }
            ret = mobile_core.set(token, ad)
            st = 'SUCCESS'
            if ret is None:
                st = 'FAILURE'
            print >> sys.stderr, "{}\t{}".format(st, line)


if __name__ == '__main__':
    import_to_admanager('test')
    #import_to_mobile_core('../../mbc')
