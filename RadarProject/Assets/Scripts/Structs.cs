
using System;
using UnityEngine;

[Serializable]
public struct ShipPrefab
{
    public ShipType shipType;
    public GameObject prefab;
}

[Serializable]
public struct WavePrefab
{
    public Waves waves;
    public GameObject prefab;
}

[Serializable]
public struct WeatherPrefab
{
    public Weather weather;
    public GameObject prefab;
    public Material skybox;
    public Material oceanMaterial; // For reflecting light from sun
}