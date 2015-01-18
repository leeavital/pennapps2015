using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using SimpleJSON;

public class json_fetcher : MonoBehaviour {


	// Use this for initialization
	IEnumerator Start () {
		Debug.Log ("Commencing HTTP");
		// Sending request:
		WWW httpResponse = new WWW("http://localhost/latest"); 
		
		// Waiting for response:
		yield return httpResponse;

		Debug.Log (httpResponse);
			Debug.Log (httpResponse.text);


		var data = JSON.Parse (httpResponse.text);

		JSONNode entityModels = data ["entityModels"].AsObject;




		Dictionary<string, GameObject> nameToObject = new Dictionary<string, GameObject> ();
		Dictionary<string, GameObject> meshDic = new Dictionary<string, GameObject> ();

		int z = 0;

		foreach(KeyValuePair<string, JSONNode> e in data["entities"].AsObject) 
		{
			Color c = Color.black;
			Debug.Log ("Insantiating: " + e.Key);
			GameObject obj = (GameObject)Instantiate(Resources.Load(entityModels[e.Key]));
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

				if(v.ToString ().Contains ("red")){
					Debug.Log ("Coloring " + obj + " red");
					c = Color.red;
				}
				else if(v.ToString().Contains("blue")){
					Debug.Log ("Coloring " + obj + " blue");
					c = Color.blue;
				}
				else if(v.ToString ().Contains("green")){
					Debug.Log ("Coloring " + obj + " green");
					c = Color.green;
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
				if(c != Color.black){
					meshFilters[i].renderer.material.color = Color.red;
				}
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
			Debug.Log (dep);
			string subject = dep[0];
			string preposition = dep[1];
			string obj = dep[2];

			float y, maximum, minimum, v, _x, _z;
			switch(preposition){
			case "prep_on":
			case "prep_on_top_of":
				// x, z are the same
				// y of object is the height of the subject + the y offset of the subject
				//float subj_size_x = meshDic[obj].renderer.bounds.size.x;
				//float subj_size_z = meshDic[obj].renderer.bounds.size.z;
//				maximum = nameToObject[obj].transform.position.x;
//				minimum = maximum - meshDic[obj].renderer.bounds.size.x;
//				v = Random.Range(minimum, maximum);

				_x = meshDic[obj].renderer.transform.position.x - (meshDic[obj].renderer.bounds.size.x / 2);
				_z = meshDic[obj].renderer.transform.position.z - (meshDic[obj].renderer.bounds.size.z / 2);
			
				y = meshDic[obj].renderer.bounds.size.y + meshDic[obj].renderer.transform.position.y;
				nameToObject[subject].transform.position 	= new Vector3(_x, y, _z);
				meshDic[subject].transform.position 		= new Vector3(_x, y, _z);
				break;

			case "prep_under":
				y = meshDic[obj].renderer.bounds.size.y;
				maximum = nameToObject[subject].transform.position.x;
				minimum = maximum - meshDic[obj].renderer.bounds.size.x;
				float y_pos = nameToObject[subject].transform.position.y;
				v = Random.Range(minimum, maximum);
				y = meshDic[obj].renderer.bounds.size.y;
				nameToObject[subject].transform.position = new Vector3(v, y_pos, v);
				break;
			case "prep_in_front_of":
				y = meshDic[obj].renderer.transform.position.y;
				_z = meshDic[obj].renderer.transform.position.z + 10;
				_x = meshDic[obj].renderer.transform.position.x;
//				meshDic[subject].renderer.transform.position = new Vector3(_x, y, _z);
				nameToObject[subject].transform.position = new Vector3(_x, y, _z);
				meshDic[subject].renderer.transform.position = new Vector3(_x, y, _z);
				break;

			case "prep_behind":
				y = meshDic[obj].renderer.transform.position.y;
				_z = meshDic[obj].renderer.transform.position.z - meshDic[obj].renderer.bounds.size.z - 10;
				_x = meshDic[obj].renderer.transform.position.x;

				nameToObject[subject].transform.position = new Vector3(_x, y, _z);
				meshDic[subject].renderer.transform.position = new Vector3(_x, y, _z);
			
				break;
			default:
				Debug.LogWarning("Unknown preposition: " + preposition);
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
