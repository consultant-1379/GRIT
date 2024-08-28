#!/bin/bash
# Build script
if [ "$2" == "" ]; then
    	echo usage: $0 \<Branch\> \<workspace\>
    	exit -1
else
	versionProperties=install/version.properties
	theDate=\#$(date +"%c")
	module=$1
	branch=$2
	workspace=$3
fi

function setVersion {

        revision=`cat $PWD/build.cfg | grep $module | grep $branch | awk -F " " '{print $4}'`

        if git tag | grep $module-$revision; then
            build_num=`git tag | grep $revision | wc -l`

	    if [ "${build_num}" -lt 10 ]; then
		build_num=0$build_num
	    fi
                version=`echo $revision$build_num | perl -nle 'sub nxt{$_=shift;$l=length$_;sprintf"%0${l}d",++$_}print $1.nxt($2) if/^(.*?)(\d+$)/';`
        else
                ammendment_level=1
                version=$revision$ammendment_level
        fi
        echo "Building version:$version"
}

function nexusDeploy {
	#RepoURL=http://eselivm2v214l.lmera.ericsson.se:8081/nexus/content/repositories/releases
	RepoURL=https://arm1s11-eiffel004.eiffel.gic.ericsson.se:8443/nexus/content/repositories/assure-releases

	GroupId=com.ericsson.eniq.events
	ArtifactId=$module
	
	echo "****"	
	echo "Deploying the zip $module.zip to Nexus...."
        	echo "****"	

  	mvn deploy:deploy-file \
	        	-Durl=${RepoURL} \
		        -DrepositoryId=assure-releases \
		        -Dpackaging=zip \
		        -DgroupId=${GroupId} \
				-Dversion=${version} \
		        -DartifactId=${ArtifactId} \
		        -Dfile=${ArtifactId}.zip
		         
 

}


setVersion
git checkout $branch
git pull origin $branch
git tag $module-$version
git push --tag origin $branch
#add ant command here
ant -file build.xml


nexusDeploy
