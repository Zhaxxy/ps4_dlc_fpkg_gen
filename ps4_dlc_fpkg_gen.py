"""
based off https://github.com/K4PS3/ps4-dlc-unlocker-maker, so credits to them
"""
from tempfile import TemporaryDirectory
from pathlib import Path
from traceback import format_exc
import random
import subprocess
import os

_MAIN_TIME_DATE = "2021-12-21 12:21:12" # idk whats special about this, but ill use it


def gen_fpkg_content_id(full_content_id: str, temp_path: Path, output_folder: Path, pubchkspath: Path) -> None:
    title_id = full_content_id.split('-')[1].split('_')[0]
    param_sfx_xml = f"""\
    <?xml version="1.0" encoding="utf-8" standalone="yes"?>
<paramsfo>
  <param key="ATTRIBUTE">0</param>
  <param key="CATEGORY">ac</param>
  <param key="CONTENT_ID">{full_content_id}</param>
  <param key="FORMAT">obs</param>
  <param key="TITLE">DLC unlocker for {full_content_id} script by Zhaxxy</param>
  <param key="TITLE_ID">{title_id}</param>
  <param key="VERSION">01.00</param>
</paramsfo>
"""
    gp4_xml = f"""\
<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<psproject fmt="gp4" version="1000">
  <volume>
    <volume_type>pkg_ps4_ac_nodata</volume_type>
    <volume_id>PS4VOLUME</volume_id>
    <volume_ts>{_MAIN_TIME_DATE}</volume_ts>
    <package content_id="{full_content_id}" passcode="00000000000000000000000000000000"/>
  </volume>
  <files img_no="0">
    <file targ_path="sce_sys/param.sfo"/>
  </files>
  <rootdir>
    <dir targ_name="sce_sys"/>
  </rootdir>
</psproject>
"""
    param_sfx = temp_path / 'param.sfx'
    gp4 = temp_path / 'dlc.gp4'
    
    param_sfx.write_text(param_sfx_xml)
    gp4.write_text(gp4_xml)
    
    sce_sys_folder = temp_path / 'sce_sys'
    sce_sys_folder.mkdir()
    
    param_sfo = sce_sys_folder / 'param.sfo'
    
    dlc_pkg_path = (output_folder / f'{full_content_id}-A0000-V0100.pkg').resolve()
    
    assert len(dlc_pkg_path.name) == (48 + 1 + 3), dlc_pkg_path
    
    result = subprocess.run((pubchkspath,'sfo_create', param_sfx, param_sfo), capture_output=True, text=True)
    
    if result.returncode:
        raise Exception(f'something went wrong with {full_content_id} param.sfo creation. {result.stdout!r}{result.stderr!r}')
    
    result = subprocess.run((pubchkspath,'img_create', '--no_progress_bar', gp4, dlc_pkg_path), capture_output=True, text=True, cwd = temp_path)
    
    if result.returncode:
        raise Exception(f'something went wrong with {full_content_id} param.sfo creation. {result.stdout!r}{result.stderr!r}')


def check_singular_cotent_id_no_start(content_id: str, /) -> bool:
    """
    This function is not foolproof! its only made to reject obvious bad data, you could easily make an invalid one that passes this
    """
    if len(content_id) != 16:
        return False
    if content_id.upper() != content_id:
        return False
    if not content_id.isalnum(): # im aware of werid unicode stuff, but we shall read the txt file in ascii anyways
        return False
    return True


def check_full_content_id(content_id: str, /) -> bool:
    """
    This function is not foolproof! its only made to reject obvious bad data, you could easily make an invalid one that passes this
    """
    if len(content_id) != 36:
        return False
    if content_id.upper() != content_id:
        return False
    
    if '-' not in content_id:
        return False
    
    if '_' not in content_id:
        return False
    
    return True


def check_content_id_starter_id(content_id: str, /) -> str | None:
    """
    check a "starter" content id and return a clean format
    This function is not foolproof! its only made to reject obvious bad data, you could easily make an invalid one that passes this
    """
    if check_full_content_id(content_id):
        return content_id.rsplit('-', 1)[0] + '-'
    if len(content_id) not in (19,20):
        return None
    return content_id if content_id.endswith('-') else content_id + '-'


def _create_task_thing(full_content_id: str, temp_path: Path, output_folder: Path, pubchkspath: Path) -> None:
    temp_path.mkdir()
    gen_fpkg_content_id(full_content_id, temp_path, output_folder, pubchkspath)


def main() -> None:
    print('based off https://github.com/K4PS3/ps4-dlc-unlocker-maker, so credits to them'.center(os.get_terminal_size().columns,'='))
    content_ids_path = Path(input('Enter the path to a new line seprated content ids txt file: '))
    
    content_ids = content_ids_path.read_text(encoding='ascii').strip().split('\n')
    
    if '-' not in content_ids[0]:
        if not all(check_singular_cotent_id_no_start(x) for x in content_ids):
            raise ValueError(f'Inconsient contend ids in {content_ids_path}, fix up yo data')
    
        start_id_input = input('Please enter the start of an example dlc id (eg UP9000-CUSA00473_00-LBPDLC2KADCO0004 or UP9000-CUSA00473_00): ').strip()
        start_id = check_content_id_starter_id(start_id_input)
        if not start_id:
            raise ValueError(f'Invalid start of dlc id {start_id_input}')
    else:
        if not all(check_full_content_id(x) for x in content_ids):
            raise ValueError(f'Invalid content ids found in {content_ids_path}, fix yo data')
        start_id = ''


    print(f'There are {len(content_ids)} content ids in {content_ids_path} to generate, example {random.choice(content_ids)}')
    if start_id:
        print(f'The start id is {start_id}, so a full id would be {start_id}{random.choice(content_ids)}, if this does not look right you ethier entered in bad data or theres a bug with this script, ethier way, exit with CRTL + C')
    
    exe_path = Path(input('Enter the path to orbis-pub-cmd, (eg Q:\e\orbis-pub-cmd.exe, im not sure about linux): '))
    
    output_fpkgs = Path(input('Finally, enter the folder path to put all the fpkgs in (leave empty and press enter for current folder, make sure the folder exists!): '))
    
    print('Lets go!')
    
    with TemporaryDirectory() as str_tp:
        tp = Path(str_tp)
        for i,x in enumerate(content_ids):
            full_content_id = start_id + x
            _create_task_thing(full_content_id,tp / str(i), output_fpkgs, exe_path)
            print(f'done pkg {i+1}/{len(content_ids)} {full_content_id}')

   
if __name__ == '__main__':
    try:
        main()
    except Exception:
        print(format_exc())
        input('Error happened, press any key to exit... ')
