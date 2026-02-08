import argparse as ap

from pipelines import SimplePipeline, ORBPipeline


def arg_parser() -> ap.Namespace:
    parser = ap.ArgumentParser(description='Image deduplication tool')
    parser.add_argument('--input_dir', '-i', type=str, help='Input directory')
    parser.add_argument('--output_file', '-o', type=str, default='./duplicates.txt', help='Output file')
    parser.add_argument(
        '--pipeline', '-p',
        type=str, default='simple',
        choices=['simple', 'orb'],
        help='Pipeline to use'
    )
    return parser.parse_args()

if __name__ == '__main__':
    args = arg_parser()

    match args.pipeline:
        case 'simple':
            pipeline = SimplePipeline(args.input_dir, args.output_file)
        case 'orb':
            pipeline = ORBPipeline(args.input_dir, args.output_file)
        case _:
            raise ValueError(f'Unknown pipeline: {args.pipeline}')

    duplicates = pipeline.run()

    with open(args.output_file, 'w') as f:
        for d in duplicates:
            f.write(f'{d[0]},{d[1]},{d[2]}\n')