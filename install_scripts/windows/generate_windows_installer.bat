@echo off

echo ####################
echo # Umit for Windows #
echo ####################
echo .

echo Setting installation variables...
set PythonEXE=C:\Python25\python.exe
set UmitOrig=C:\Umit\trunk
set UmitDir=C:\UmitTemp
set DistDir=%UmitDir%\dist
set GTKDir=C:\GTK
set NmapDir=C:\Nmap
set WinpcapDir=C:\Winpcap
set WinInstallDir=%UmitDir%\install_scripts\windows
set Output=%UmitDir%\win_install.log
set MakeNSIS=C:\NSIS\makensis.exe
set UtilsDir=%UmitDir%\install_scripts\utils

echo Writing output to %Output%
rd %Output% /S /Q

echo Removing old compilation...
rd %UmitDir% /S /Q

echo Creating a temp directory for compilation...
mkdir %UmitDir%

echo Copying trunk to the temp dir...
xcopy %UmitOrig%\*.* %UmitDir% /E /S /C /Y /V /I >> %Output%

echo Creating dist and dist\share directories...
mkdir %DistDir%\share
mkdir %DistDir%\share\gtk-2.0
mkdir %DistDir%\share\gtkthemeselector
mkdir %DistDir%\share\themes
mkdir %DistDir%\share\xml


echo Copying GTK's share to dist directory...
xcopy %GTKDir%\share\gtk-2.0\*.* %DistDir%\share\gtk-2.0\ /S >> %Output%
xcopy %GTKDir%\share\gtkthemeselector\*.* %DistDir%\share\gtkthemeselector\ /S >> %Output%
xcopy %GTKDir%\share\themes\*.* %DistDir%\share\themes\ /S >> %Output%
xcopy %GTKDir%\share\xml\*.* %DistDir%\share\xml\ /S >> %Output%


echo Creating Nmap dist dirs...
mkdir %DistDir%\Nmap


echo Copying Nmap to his dist directory...
xcopy %NmapDir%\*.* %DistDir%\Nmap >> %Output%


echo Compiling Umit using py2exe...
cd %UmitDir%
%PythonEXE% -OO %WinInstallDir%\setup.py py2exe >> %Output%

echo Copying some more GTK files to dist directory...
xcopy %GTKDir%\lib %DistDir%\lib /S /I >> %Output%
xcopy %GTKDir%\etc %DistDir%\etc /S /I >> %Output%


echo Removing the build directory...
rd %UmitDir%\build /s /q >> %Output%

echo .
echo Creating installer...
%MakeNSIS% /P5 /V4 /NOCD %WinInstallDir%\umit_compiled.nsi

cd %UmitOrig%
echo Done!
