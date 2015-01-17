using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using SimpleJSON;

public class json_fetcher : MonoBehaviour {


	// Use this for initialization
	IEnumerator Start () {
		Debug.Log ("Commencing HTTP");
		// Sending request:
		WWW httpResponse = new WWW("http://127.0.0.1/latest"); 
		
		// Waiting for response:
		yield return httpResponse;

		Debug.Log (httpResponse);
		Debug.Log (httpResponse.text);


		var data = JSON.Parse (httpResponse.text);



		Debug.Log (data ["entities"].AsObject);

		Dictionary<string, GameObject> nameToObject = new Dictionary<string, GameObject> ();
		Dictionary<string, GameObject> meshDic = new Dictionary<string, GameObject> ();

		int z = 0;

		foreach(KeyValuePair<string, JSONNode> e in data["entities"].AsObject) 
		{	
			Debug.Log ("Insantiating: " + e.Key);
			GameObject obj = (GameObject)Instantiate(Resources.Load(e.Key));
			// e.value is a list of qualifiers (i.e. book: ["red"])
			// cube.AddComponent<Rigidbody>();
			obj.transform.position = new Vector3(0, 0, 0);
			foreach(JSONNode v in e.Value.AsArray){
				Debug.Log (v.ToString());
				if(v.ToString().Contains("big")){
					obj.transform.localScale += new Vector3(1.5f,1.5f,1.5f);
				}
				if(v.ToString().Contains("small")){
					obj.transform.localScale -= new Vector3(1.5f,1.5f,1.5f);
				}
				//		if(v..Equals("big")){
				//}
			}
			GameObject pico = GameObject.CreatePrimitive(PrimitiveType.Cube);
			MeshFilter[] meshFilters = obj.GetComponentsInChildren<MeshFilter>();
			CombineInstance[] combine = new CombineInstance[meshFilters.Length];

			for (int i = 0; i < meshFilters.Length; i++) {
				combine[i].mesh = meshFilters[i].sharedMesh;
				combine[i].transform = meshFilters[i].transform.localToWorldMatrix;
			}
			
			pico.GetComponent<MeshFilter>().mesh = new Mesh();
			pico.transform.GetComponent<MeshFilter>().mesh.CombineMeshes(combine);
			pico.renderer.enabled = false;
			Debug.Log(e.Key);
			nameToObject[e.Key] = obj;
			meshDic[e.Key] = pico;
		}


		foreach(JSONNode dep in data ["deps"].AsArray)
		{
			Debug.Log(dep);
			string subject = dep[0];
			string preposition = dep[1];
			string obj = dep[2];

			float y, maximum, minimum, v;
			switch(preposition){
			case "prep_on":
			case "prep_on_top_of":
				// x, z are the same
				// y of object is the height of the subject
				//float subj_size_x = meshDic[obj].renderer.bounds.size.x;
				//float subj_size_z = meshDic[obj].renderer.bounds.size.z;
				maximum = nameToObject[subject].transform.position.x;
				minimum = maximum - meshDic[obj].renderer.bounds.size.x;
				Debug.Log (minimum);
				Debug.Log(maximum);
				v = Random.Range(minimum, maximum);
				Debug.Log(v);
				y = meshDic[obj].renderer.bounds.size.y;
				Debug.Log(y);
				nameToObject[subject].transform.position = new Vector3(v, 1 * y, v);
				break;

			case "prep_under":
				y = meshDic[obj].renderer.bounds.size.y;
				Debug.Log(y);
				maximum = nameToObject[subject].transform.position.x;
				minimum = maximum - meshDic[obj].renderer.bounds.size.x;
				float y_pos = nameToObject[subject].transform.position.y;
				v = Random.Range(minimum, maximum);
				y = meshDic[obj].renderer.bounds.size.y;
				nameToObject[subject].transform.position = new Vector3(v, y_pos, v);
				break;
			}
		}

	
		
		
		
	}



	// Update is called once per frame
	void Update () {
		float xAxisValue = Input.GetAxis("Horizontal");
		float zAxisValue = Input.GetAxis("Vertical");
		float yAxisValue = Input.GetAxis ("Mouse Y");
		if(Camera.current != null)
		{
			Camera.current.transform.Translate(new Vector3(xAxisValue, yAxisValue, zAxisValue));
		}
	}
}
