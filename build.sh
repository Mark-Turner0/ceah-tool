rm -fr build dist
rm -fr ~/Library/Containers/uk.markturner.ceah-tool/
pyi-makespec main.py -n "Cyber Essentials at Home" --add-data scripts:scripts --add-data imgs:imgs -w -i     imgs/logo.ico --version-file 0.1 --osx-bundle-identifier uk.markturner.ceah-tool
sed '$ s/.$/,/' "Cyber Essentials at Home.spec" > temp
cat temp resources/ceah.spec > "Cyber Essentials at Home.spec"
rm -f temp
pyinstaller --noconfirm "Cyber Essentials at Home.spec"
chmod +x resources/postinstall
cd dist
rm -fr "Cyber Essentials at Home"
codesign --entitlements ../resources/.entitlements -fs - "Cyber Essentials at Home.app"
pkgbuild --identifier uk.markturner.ceah-tool --install-location /Applications --root ./ --component-plist ../resources/ceah-tool.plist --scripts ../resources --ownership preserve component.pkg
productbuild --distribution ../resources/distribution.xml "./Cyber Essentials at Home.pkg"
