"""Publish the prepared mapped golden dataset and verify the committed files."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tempfile

from huggingface_hub import DatasetCard, HfApi, hf_hub_download

ROOT = Path(__file__).resolve().parents[1]
FILES = ['README.md', 'golden.parquet']
SUPPLEMENTARY_FILES = ['golden.jsonl', 'candidates.parquet', 'manifest.json',
    'label_representation.csv', 'label_representation.json', 'label_representation.md']


def portable(value):
    """Remove local checkout prefixes from published provenance paths."""
    if isinstance(value,str): return value.replace(str(ROOT)+'/', '')
    if isinstance(value,list): return [portable(item) for item in value]
    if isinstance(value,dict): return {portable(key):portable(item) for key,item in value.items()}
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-id',default='yasalma/mapped-crawlres-fineweb')
    parser.add_argument('--dataset-dir',type=Path,default=ROOT/'golden_crawlres_fineweb')
    args = parser.parse_args()
    for name in FILES:
        if not (args.dataset_dir/name).is_file(): raise FileNotFoundError(name)
    card = DatasetCard.load(args.dataset_dir/'README.md')
    assert {config['config_name'] for config in card.data.to_dict()['configs']} == {'golden'}
    assert '{{' not in card.content
    with tempfile.TemporaryDirectory(prefix='mapped-golden-publish-') as directory:
        staged = Path(directory)
        for name in FILES: shutil.copy2(args.dataset_dir/name,staged/name)
        api = HfApi()
        api.create_repo(repo_id=args.repo_id,repo_type='dataset',private=False,exist_ok=True)
        commit = api.upload_folder(repo_id=args.repo_id,repo_type='dataset',folder_path=staged,
            allow_patterns=FILES,delete_patterns=SUPPLEMENTARY_FILES,
            commit_message='Keep only the main golden dataset and its description')
        info = api.dataset_info(args.repo_id,revision=commit.oid,files_metadata=True)
        remote = {item.rfilename:item for item in info.siblings}
        assert not set(SUPPLEMENTARY_FILES) & set(remote)
        for name in FILES:
            local = staged/name
            assert name in remote, name
            assert remote[name].size == local.stat().st_size, name
            lfs = remote[name].lfs
            if lfs:
                assert lfs.sha256 == hashlib.sha256(local.read_bytes()).hexdigest(), name
            else:
                downloaded = hf_hub_download(args.repo_id,name,repo_type='dataset',revision=commit.oid)
                assert Path(downloaded).read_bytes() == local.read_bytes(), name
        result = dict(repo_id=args.repo_id,url=f'https://huggingface.co/datasets/{args.repo_id}',
            revision=commit.oid,verified_files=FILES,private=info.private)
        (args.dataset_dir/'publication.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(result,indent=2),flush=True)


if __name__ == '__main__':
    main()
