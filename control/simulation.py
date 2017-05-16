#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: Jan Hybs


from os.path import join, realpath
import yaml
import progressbar
import time
import sys
import datetime

__dir__ = realpath(__file__)
__root__ = realpath(join(__dir__, '../' * 2))
__bench__ = realpath(join(__root__, 'benchmarks'))


main_hh_template = realpath(join(__bench__, 'main.template.hh'))
main_hh = realpath(join(__bench__, 'main.hh'))
version = realpath(join(__root__, 'version'))
versions_yaml = realpath(join(__root__, 'versions.yaml'))
log_txt = realpath(join(__root__, 'log.' + str(time.time())+'.txt'))


from configure import new_version


class Logger(object):
    @staticmethod
    def write(msg=None, *msgs):
        with open(log_txt, 'a') as fp:
            if msg is not None:
                fp.write(str(datetime.datetime.utcnow()) + ': ')
                fp.write(str(msg))
                print(msg, end='')

                for m in msgs:
                    fp.write('\n' + str(m))
                    print('\n' + str(m), end='')
            fp.write('\n')
            print('')

    @staticmethod
    def flush(*args, **kwargs):
        pass


def unwind_versions(versions):
    final_versions = list()  # type: list[dict]
    prev_version = None      # type: dict

    for version in versions['versions']:
        # accept blindly first version
        if prev_version is None:
            prev_version = version
            final_versions.append(version)
            continue

        if type(version) is str:
            version = {version:None}

        version_name = str(list(version.keys())[0])
        if version_name.find('[') != -1:
            #  process smh like 1.0.[1-15]
            f, t = (version_name.split('.')[-1][1:-1]).split('-')  # type: str
            rng = range(int(f.strip()), int(t.strip())+1)
        else:
            rng = [int(version_name.split('.')[-1])]

        for v in rng:
            version_name_full = '.'.join(version_name.split('.')[0:2] + [str(v)])
            variables = list(prev_version.values())[0].copy()

            for overrides in list(version.values()):
                if overrides is None:
                    break
                for key, override in overrides.items():
                    if type(override) is str:
                        if override.startswith('+'):
                            override = int(variables[key] + float(override[2:]))
                        elif override.startswith('-'):
                            override = int(variables[key] - float(override[2:]))
                        elif override.startswith('x'):
                            override = int(variables[key] * float(override[2:]))
                        elif override.startswith('/'):
                            override = int(variables[key] / float(override[2:]))

                    variables[key] = override
            full_version = {version_name_full: variables}
            prev_version = full_version
            final_versions.append(full_version)

    return final_versions


version_list = unwind_versions(yaml.load(open(versions_yaml, 'r')))

# Logger.write(yaml.dump(version_list, default_flow_style=False))
Logger.write('total versions: %d' % len(version_list))
Logger.write()

if __name__ == '__main__':
    wait_time = 100 # 60*60*1 # one hour
    current_wait = 0
    version_index = 0
    sleep_amount = 5
    max_version = len(version_list)

    for current_version in version_list[version_index:max_version]:
        variables = list(current_version.values())[0]
        version_name = list(current_version.keys())[0]

        vars_log = yaml.dump(variables, default_flow_style=False)
        Logger.write('{version_index:3d} / {max_version:3d} - {version_name}'.format(**locals()), vars_log)

        # create new version
        new_version(variables, version_name)

        if version_index == max_version:
            Logger.write('All jobs completed')
            break

        Logger.write('Sleeping for %d seconds' % wait_time)
        with progressbar.ProgressBar(max_value=wait_time, fd=sys.stdout) as pb:
            for i in range(0, wait_time, sleep_amount):
                pb.update(i)
                time.sleep(sleep_amount/100.)
            Logger.write('Done sleeping')
            Logger.write()
        version_index += 1