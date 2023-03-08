import os
import json
import re
from workspace import Workspace

settings=[{"imagefile":"29bf524180d498425f1fae871e42ea1624447edb.png","title":"About","arg":"x-apple.systempreferences:com.apple.SystemProfiler.AboutExtension"},
        {"imagefile":"9dd8742fe2ff502b63a645c74115ec318e59232d.png","title":"Accessibility","arg":"x-apple.systempreferences:com.apple.preference.universalaccess"},
        {"imagefile":"6d2268100b3681393461496a6eba7daf0ce6f24c.png","title":"AirDrop & Handoff","arg":"x-apple.systempreferences:com.apple.AirDrop-Handoff-Settings.extension"},
        {"imagefile":"b23606c5a7e9d006774de6bba3cc6e8d23eb7c6f.png","title":"Appearance","arg":"x-apple.systempreferences:com.apple.Appearance-Settings.extension"},
        {"imagefile":"e9046ca8c02c1a7181bfb308b28d49a09d1875eb.png","title":"Apple ID","arg":"x-apple.systempreferences:com.apple.preferences.AppleIDPrefPane"},
        {"imagefile":"95c4617aa79be5d0b87ad7513f97cd1b6d97959a.png","title":"Battery","arg":"x-apple.systempreferences:com.apple.preference.battery"},
        {"imagefile":"5f6447eb3c6eb47e26123ff2a4f4ee74c71fc9b6.png","title":"Bluetooth","arg":"x-apple.systempreferences:com.apple.BluetoothSettings"},
        {"imagefile":"bea1cb4a6bc637076c21779c4e5fd6e5a9093936.png","title":"Control Centre","arg":"x-apple.systempreferences:com.apple.ControlCenter-Settings.extension"},
        {"imagefile":"443b07f2bbc807da271beba7362f29b7cdbac073.png","title":"Date & Time","arg":"x-apple.systempreferences:com.apple.preference.datetime"},
        {"imagefile":"ba4c7a5af72805e21bae46e2433ca61eb6477c9c.png","title":"Desktop & Dock","arg":"x-apple.systempreferences:com.apple.Desktop-Settings.extension"},
        {"imagefile":"a1b92d6c8cf708253dc9118c850bfd45fb8dd0a9.png","title":"Displays","arg":"x-apple.systempreferences:com.apple.Displays-Settings.extension"},
        {"imagefile":"91e4ff9aaf974325f6770323f61f16f6cc4b5d29.png","title":"Extensions","arg":"x-apple.systempreferences:com.apple.preferences.extensions"},
        {"imagefile":"07ae85f266b9c24297b6b095b72975a8f8e4eb42.png","title":"Family","arg":"x-apple.systempreferences:com.apple.preferences.FamilySharingPrefPane","subtitle":""},
        {"imagefile":"44a74b20468e31358b616173504bbf7b15e9d3bf.png","title":"Focus","arg":"x-apple.systempreferences:com.apple.Focus-Settings.extension"},
        {"imagefile":"00fd1ae0a9d063bd68be6be831f2c582fcffed38.png","title":"Game Centre","arg":"x-apple.systempreferences:com.apple.Game-Center-Settings.extension"},
        {"imagefile":"24be727b5d106827a882dcc899454491cebd7644.png","title":"Game Controllers","arg":"x-apple.systempreferences:com.apple.Game-Controller-Settings.extension"},
        {"imagefile":"1c2a39142d530677525ca067a60f7360f6a5329f.png","title":"General","arg":"x-apple.systempreferences:com.apple.systempreferences.GeneralSettings"},
        {"imagefile":"40b4c7d9783284fe28dae19503db8255e30044f7.png","title":"iCloud","arg":"x-apple.systempreferences:com.apple.preferences.AppleIDPrefPane?iCloud"},
        {"imagefile":"213eabfbe8019cd7719939859a04acb7468e56ca.png","title":"Internet Accounts","arg":"x-apple.systempreferences:com.apple.Internet-Accounts-Settings.extension"},
        {"imagefile":"13e1f22e0fe9142301858c3da4284eec9eb8e550.png","title":"Keyboard","arg":"x-apple.systempreferences:com.apple.Keyboard-Settings.extension"},
        {"imagefile":"a066803da328acb15d88be4b45c0e7daab1a1c39.png","title":"Languages & Region","arg":"x-apple.systempreferences:com.apple.Localization-Settings.extension"},
        {"imagefile":"db7f6077f9dfc903e861f2f4fe51ca474e41fa93.png","title":"Lock Screen","arg":"x-apple.systempreferences:com.apple.Lock-Screen-Settings.extension"},
        {"imagefile":"2f1a9e8282de2342b0169618810927912086523a.png","title":"Login Items","arg":"x-apple.systempreferences:com.apple.LoginItems-Settings.extension"},
        {"imagefile":"6bb33971f6acf642bd94320cac1e98a3295f58e4.png","title":"Mouse","arg":"x-apple.systempreferences:com.apple.Mouse-Settings.extension"},
        {"imagefile":"2aa0206c36bb46a09d75235d3b0f618888580a42.png","title":"Network","arg":"x-apple.systempreferences:com.apple.Network-Settings.extension"},
        {"imagefile":"1d23e371c440469a53bfbe60df4c9769e530729b.png","title":"Notifications","arg":"x-apple.systempreferences:com.apple.preference.notifications"},
        {"imagefile":"6f564f14ec4084a9fb682408bd9e1223394d236e.png","title":"Passwords","arg":"x-apple.systempreferences:com.apple.Passwords-Settings.extension"},
        {"imagefile":"f70c7c5124830569df29032024a630c1663e5cb6.png","title":"Printers & Scanners","arg":"x-apple.systempreferences:com.apple.Print-Scan-Settings.extension"},
        {"imagefile":"182db20292e160b015f59ea7123d3dcda4dd1367.png","title":"Privacy & Security","arg":"x-apple.systempreferences:com.apple.preference.security"},
        {"imagefile":"38a712d5e6e851ec6620eb3453fc57360d64b165.png","title":"Profiles","arg":"x-apple.systempreferences:com.apple.preferences.configurationprofiles"},
        {"imagefile":"407042bdcecf4651c695a913dddd00d148bd6405.png","title":"Screen Saver","arg":"x-apple.systempreferences:com.apple.ScreenSaver-Settings.extension"},
        {"imagefile":"68f5d276618cbd1ffc5c23e1d80549aaeaff3ea5.png","title":"Screen Time","arg":"x-apple.systempreferences:com.apple.preference.screentime"},
        {"imagefile":"9b4439cebdf1564ef637b6bcab2ae4a0a02d8fbe.png","title":"Sharing","arg":"x-apple.systempreferences:com.apple.preferences.sharing"},
        {"imagefile":"2889b79312472914f44e612e06c528de1c81ccd2.png","title":"Siri & Spotlight","arg":"x-apple.systempreferences:com.apple.preference.speech"},
        {"imagefile":"2b66c568b4720e8c13d8883d2c4f0d038a99eab0.png","title":"Software Update","arg":"x-apple.systempreferences:com.apple.preferences.softwareupdate"},
        {"imagefile":"44dcd0f8e8a4859f7c801b731ed96b8f26d5b2e9.png","title":"Sound","arg":"x-apple.systempreferences:com.apple.Sound-Settings.extension"},
        {"imagefile":"cc1c2cdec516d3f262bf9d2b68e291b929f1481c.png","title":"Startup Disk","arg":"x-apple.systempreferences:com.apple.Startup-Disk-Settings.extension"},
        {"imagefile":"274a7034fbd6df9e540589f749b6e788a7cb2c37.png","title":"Storage","arg":"x-apple.systempreferences:com.apple.settings.Storage"},
        {"imagefile":"8be80f66c735b9215f033176ca3a1f10b9eee647.png","title":"Time Machine","arg":"x-apple.systempreferences:com.apple.Time-Machine-Settings.extension"},
        {"imagefile":"ba1f93b828dd0fb3d1e560f4c6136c2559085c07.png","title":"Touch ID & Password","arg":"x-apple.systempreferences:com.apple.preferences.password"},
        {"imagefile":"e16de3bc677c439757e0e8afdf4ed335c62e5fac.png","title":"Trackpad","arg":"x-apple.systempreferences:com.apple.Trackpad-Settings.extension"},
        {"imagefile":"562e1db55f551f25aaad5b5fe6bc093db6c7cbdf.png","title":"Transfer or Reset","arg":"x-apple.systempreferences:com.apple.Transfer-Reset-Settings.extension"},
        {"imagefile":"1fb87c68a8c5473b9cfc5022c73368028e96ea60.png","title":"Users & Groups","arg":"x-apple.systempreferences:com.apple.Users-Groups-Settings.extension"},
        {"imagefile":"21f335082f40c41dff1579577159589bb82dc2f0.png","title":"VPN","arg":"x-apple.systempreferences:com.apple.NetworkExtensionSettingsUI.NESettingsUIExtension"},
        {"imagefile":"58452ec64450c056f855996170876cad614a74d3.png","title":"Wallet & Apple Pay","arg":"x-apple.systempreferences:com.apple.WalletSettingsExtension"},
        {"imagefile":"8296e25ce05a54f648f7a681e1ce0f201ba7e4fc.png","title":"Wallpaper","arg":"x-apple.systempreferences:com.apple.Wallpaper-Settings.extension"},
        {"imagefile":"4f910d01bf9e0ef305504af1ca3e271ad1ad9ce0.png","title":"Wi-Fi","arg":"x-apple.systempreferences:com.apple.wifi-settings-extension"}]

def multi_contain(total,parts):
    totle_low=total.lower()
    for p in parts:
        if p.lower() not in totle_low:
            return False
    return True

# 解决循环中的闭包问题
def wrapper(arg):
    def open_url():
        os.system('open "%s"' % arg)
    return open_url

def search(name):
    results=[]
    name=re.split("\s",name.strip())
    def find_setting(item,arg):
        title = item["title"]
        sub_title = title
        if multi_contain(title,name):
            action=wrapper(item["arg"])
            results.append(Workspace(title,sub_title,action,icon="images/system_setting/"+item["imagefile"]))
    for item in settings:
        find_setting(item,"")
    return results
