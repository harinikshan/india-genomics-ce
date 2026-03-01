from pathlib import Path

from scripts.vcf_to_23andme import convert_vcf_to_23andme


def test_convert_vcf_to_23andme_basic(tmp_path: Path):
    vcf = tmp_path / "sample.vcf"
    out = tmp_path / "out.txt"

    vcf.write_text(
        "\n".join(
            [
                "##fileformat=VCFv4.2",
                "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tSAMPLE",
                "1\t101\trs111\tA\tG\t100\tPASS\t.\tGT\t0/1",
                "1\t102\t.\tC\tT\t100\tPASS\t.\tGT\t0/1",
                "1\t103\trs113\tA\tAT\t100\tPASS\t.\tGT\t0/1",
                "1\t104\trs114\tG\tA\t100\tPASS\t.\tGT\t1/1",
            ]
        ),
        encoding="utf-8",
    )

    converted = convert_vcf_to_23andme(str(vcf), str(out))
    assert converted == 2

    lines = out.read_text(encoding="utf-8").splitlines()
    body = [line for line in lines if not line.startswith("#")]
    assert len(body) == 2
    assert body[0].startswith("rs111\t1\t101\tAG")
    assert body[1].startswith("rs114\t1\t104\tAA")
