cd tools
rm -rf annatto
git clone https://github.com/korpling/annatto.git
cd annatto
cargo build --release
cp target/release/annatto ../../
cd ../..
rm -rf tools/annatto
git commit annatto -m 'updated annatto'
