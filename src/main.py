#-*- coding:utf-8 -*-



import kibana_api
import resas_elastic

def main():
	ig = kibana_api.IndexPatternGenerator()
	vg = kibana_api.VisualizationGenerator()

	ka = kibana_api.KibanaAPI()
	ea = kibana_api.ElasticAPI()



if __name__=="__main__":
	main()
