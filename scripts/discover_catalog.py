import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from goodsdex.catalog_discovery import run
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path('_data'))
    parser.add_argument('categories',nargs='*')
    args=parser.parse_args();result=run(args.root,args.categories)
    print(json.dumps({k:v for k,v in result.items() if k!='categories'},ensure_ascii=False))
