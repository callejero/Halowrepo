rbutton::
    gst:=Mouse_Gesture()
    if (gst="ldrdl")
        soundbeep
    else if (gst)
        traytip,Mouse_Gesture returns:,% gst
    return  

Mouse_Gesture(Button="",dt=50,dv=0.040,ds=5,TabTime=150,SendButton=1)
	{
	static u:=[0,0], tf:={"u":[-1,2,1],"d":[1,2,1],"l":[-1,1,2],"r":[1,1,2]}
	mousegetpos,x0,y0
	cnt:=0
	gesture:=""
	sl:=ceil(ds/(dv*dt))
	x00:=x0
	y00:=y0
	Button:=Button="" ? regexreplace(a_thishotkey,"\W") : Button
	
	while (GetKeyState(Button,"P"))
		{
		sleep,% dt
		cnt++
		mousegetpos,x1,y1
		u.1:=x1-x0, u.2:=y1-y0, x0:=x1, y0:=y1
		if (u.1**2+u.2**2>(dv*dt)**2)
			for sct, p in tf
				if (p.1*u[p.2]>abs(u[p.3]))
					{
					gesture.=sct
					break
					}
		}
	
	if (SendButton && cnt && cnt*dt<=TabTime)
		{
		send,% "{" Button "}"
		return, 0
		}
		
	mousemove,x00,y00,1
	return regexreplace(regexreplace(regexreplace(regexreplace(gesture, "(u{" sl ",}|d{" sl ",}|l{" sl ",}|r{" sl ",})","$T1"),"u|d|l|r"),"i)(u+|d+|l+|r+)","$T1"),"u|d|l|r")
	}