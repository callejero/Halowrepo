;
; AutoHotKey Script for Viaplay XBMC Plugin
; Version 2.0
;
#SingleInstance force
#Persistent
IniRead, WaitPlaybackVar, Settings.ini, Settings, WaitPlayback


DetectHiddenWindows, on
SetTitleMatchMode 2
SetBatchLines, -1
Process, Priority,, High

	Send {Media_Stop}	

	IfWinExist, ahk_class XBMC
	{
		WinMinimize
	}

	IfWinExist, ahk_class Kodi
	{
		WinMinimize
	}


	if WinExist("viaplay.")
	{
	    WinActivate  ; Automatically uses the window found above.
	    WinMaximize  ; same	

	}	

	WinWaitActive, Viaplay
	sleep 2000
	send {F11}

	
	sleep %WaitPlaybackVar%
	MouseMove, 600, 380
	Click	

	sleep 10000

	MouseGetPos, xpos, ypos 
	
	xnew:=(A_ScreenWidth /2)
	ynew:=220
	
	MouseMove, xnew, ynew
	Click 2
	sleep 500
	
	MouseMove, xpos, ypos
	

sleep 2000

loop
{
	sleep 1000
	WinGetTitle, Title, A
	
	
	if WinActive("Microsoft Silverlight")
	{
		
		Gui +LastFound
		hWnd := WinExist()
		
		DllCall( "RegisterShellHookWindow", UInt,hWnd )
		MsgNum := DllCall( "RegisterWindowMessage", Str,"SHELLHOOK" )
		OnMessage( MsgNum, "ShellMessage" )
		Return
		
		ShellMessage( wParam,lParam ) 
		{
			If ( wParam = 12 )
			{
				
				value :=(lParam>>16)
				
				if(value=4143) ; pause
				{
					;SendInput {Space}
					PlayPause()
				}
				else if(value=4142) ;play
				{
					;SendInput {Space}
					PlayPause()
				}
				else if(value=14) ;toggle play/pause
				{
					;SendInput {Space}
					PlayPause()
				}
				else if(value=-32767) ;back
				{
					;SendInput {Esc}
					
					StopPlayback()
				}
				else if(value=13) ;stop
				{
					
					StopPlayback()
				}
				else if(value=12) ;replay
				{
					Replay()
					
				}
				else if(value=11) ;skip
				{
					ContinuePlayback()
				}
				else if(value=4147) ;channel up
				{
					ShowQuality()
				}
				;MsgBox, , test, % value
			}
		}
		
		^+S:: StopPlayback() ;Stop
		return
		^+F:: ContinuePlayback() ;Forward
		return
		^+B:: Replay() ;Skip
		return
		x::
		BackSpace:: StopPlayback()
		return
		
		#ifWinActive viaplaylauncher
		Enter:: ToggleFullscreen()
		return
		
		#ifWinActive ahk_class MicrosoftSilverlight
		BackSpace:: ToggleFullscreen()
		return
		^+P:: SendInput {Space} ;Play
		return
		Q:: SendInput {Space} ;Pause
		return
		^+S:: StopPlayback() ;Stop
		return
		^+B:: ShowQuality() ;Set bitrate
		return
	}
	
}

ToggleFullscreen()
{
	MouseGetPos, xpos, ypos 
	
	xnew:=(A_ScreenWidth /2)
	ynew:=220
	
	MouseMove, xnew, ynew
	Click 2
	sleep 500
	
	MouseMove, xpos, ypos
}

ShowQuality()
{
	MouseGetPos, xpos, ypos 
	
	xnew:=A_ScreenWidth-115
	ynew:=A_ScreenHeight-50
	
	MouseMove, xnew, ynew
	Click
	sleep 500
	
	xnew:=A_ScreenWidth-120
	ynew:=A_ScreenHeight-255
	
	MouseMove, xnew, ynew
	Click
	sleep 500
	
	MouseMove, xpos, ypos
	Click
	
}

Replay()
{
	MouseGetPos, xpos, ypos 
	
	xnew:=(A_ScreenWidth /2)-60
	ynew:=380 ;A_ScreenHeight
	
	MouseMove, xnew, ynew
	Click
	sleep 500
	
	MouseMove, xpos, ypos
	
	
}
PlayPause()
{
	
	MouseGetPos, xpos, ypos 
	
	xnew:=45
	ynew:=A_ScreenHeight-50
	
	MouseMove, xnew, ynew
	Click
	sleep 500
	
	MouseMove, xpos, ypos
	
}

ContinuePlayback()
{
	MouseGetPos, xpos, ypos 
	
	xnew:=(A_ScreenWidth /2)+120
	ynew:=380 ;A_ScreenHeight
	
	MouseMove, xnew, ynew
	Click
	sleep 500
	
	MouseMove, xpos, ypos
}

StartFullscreen()
{

	WinWaitActive, Viaplay - Internet Explorer

	sleep 10000

	WinGet, IEControlList, ControlList, ahk_class IEFrame
	Loop, Parse,IEControlList, `n
	{
    		;MsgBox, 4,, Control #%a_index% is "%A_LoopField%"
    		if (A_LoopField = "MicrosoftSilverlight1")
    		{
        		;MsgBox, MicrosoftSilverlight1 control exists in IEFrame window so do the rest of your stuff here

			MouseGetPos, xpos, ypos 
	
			xnew:=(A_ScreenWidth /2)
			ynew:=220
	
			MouseMove, xnew, ynew
			Click 2
			sleep 500
	
			MouseMove, xpos, ypos

    		}    
	}

}

StopPlayback()
{
	
	PlayPause()
	
	sleep 250

	SendInput {Esc}

	sleep 250

	SendInput {LAlt Down}{F4 down}{F4 up}{LAlt Up}

	if WinExist("ahk_class MicrosoftSilverlight") or WinExist("Viaplay - Internet Explorer") or WinExist("Microsoft Silverlight") or WinExist("http://viaplay.") 
	{
		WinActivate  ; Automatically uses the window found above.
		;MsgBox, , test, "Microsoft Silverlight"
		;WinClose, A
		WinKill
	}


	sleep 250

	if WinExist("http://viaplay.")
	{
		winkill
	}

	
	IfWinExist, ahk_class XBMC
	{
		WinActivate
		WinMaximize 
	}

	IfWinExist, ahk_class Kodi
	{
		WinActivate 
		WinMaximize
	}
	
	ExitApp
	
}
