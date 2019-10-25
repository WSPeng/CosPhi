	sprintf(buffer,"Detected %i of %i at %ld \n",numFound,numObjects,updateTime);
	STrackedObject o;
	for (int i=0;i<numObjects;i++){
		o=object[i];
		sprintf(buffer,"%sRobot %03i %.3f %.3f %.3f %ld \n",buffer,o.ID,o.x,o.y,o.yaw*180/M_PI,lastDetectionArray[i]);
	}
	if (calibrationFinished)
	{
		sprintf(buffer,"%sCalibrated\n",buffer);
		calibrationFinished = false;
	}