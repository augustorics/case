
Código pensado para adaptador MKS CANable V2.0. A equipe planeja desenvolver um, dependendo dos drivers será necessário atualizar o script em python.
https://pt.aliexpress.com/item/1005006841178138.html?spm=a2g0o.detail.pcDetailBottomMoreOtherSeller.1.5edencX6ncX6hX&gps-id=pcDetailBottomMoreOtherSeller&scm=1007.40050.354490.0&scm_id=1007.40050.354490.0&scm-url=1007.40050.354490.0&pvid=95bb215c-0c99-4fb1-b5be-b4988678ae1e&_t=gps-id:pcDetailBottomMoreOtherSeller,scm-url:1007.40050.354490.0,pvid:95bb215c-0c99-4fb1-b5be-b4988678ae1e,tpp_buckets:668%232846%238107%231934&isseo=y&pdp_ext_f=%7B%22order%22%3A%2258%22%2C%22eval%22%3A%221%22%2C%22sceneId%22%3A%2230050%22%7D&utparam-url=scene%3ApcDetailBottomMoreOtherSeller%7Cquery_from%3A#nav-specification

https://pt.aliexpress.com/item/1005006842262016.html?spm=a2g0o.productlist.main.5.4dec40311yJWF2&algo_pvid=cbb2e518-d27f-4081-9e64-ebc938b1edd0&pdp_ext_f=%7B%22order%22%3A%22346%22%2C%22eval%22%3A%221%22%7D&utparam-url=scene%3Asearch%7Cquery_from%3A

https://pt.aliexpress.com/item/1005008500955467.html?spm=a2g0o.productlist.main.1.4dec40311yJWF2&algo_pvid=cbb2e518-d27f-4081-9e64-ebc938b1edd0&pdp_ext_f=%7B%22order%22%3A%22114%22%2C%22eval%22%3A%221%22%7D&utparam-url=scene%3Asearch%7Cquery_from%3A


Reset:
Para o reset na ECU desejada na aplicação principal da ECU deve conter um #define ECU_ID 0x01...

a função a baixo é um exemplo do que deve estar na aplicação principal para que ela faça o reset.

	void HAL_CAN_RxFifo0MsgPendingCallback(CAN_HandleTypeDef *hcan){
	    CAN_RxHeaderTypeDef RxHeader;
	    uint8_t RxData[8];
	
	    HAL_CAN_GetRxMessage(hcan, CAN_RX_FIFO0, &RxHeader, RxData);
	
	    uint8_t destino = RxData[0];
	    if (destino != ECU_ID)
	        return;
	
	    if (RxHeader.StdId == 0x0F0) // comando RESET
	    {        
	        NVIC_SystemReset();
	    }
	}



Adaptador CAN real:

- Quando conectado verificar no windows qual porta COM ele esta ex. COM1 COM2 ... e alterar no script na definição de CHANNEL logo no início

firmware.bin:

- Também no início do código deve ser definido o endereço correto para o firmware.bin para a ECU desejada, dentro da matriz ECUS = {} 

IDs:

- Devem bater com os definidos dentro dos bootloader/aplicações principais para que os comando sejam enviados para a ECU correta, configurar na mesma matriz ECU = {}
