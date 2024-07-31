package actas

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"

	"github.com/pkg/errors"
	"github.com/samber/lo"
)

var apiEndpoint = "https://gdp.theempire.tech/api/data"

type CedulaInfo struct {
	Cedula string

	// demographic info, omitted for now

	StateID   string
	StateName string

	CountyID   string
	CountyName string

	ParishID   string
	ParishName string

	CenterOldID   string
	CenterID      string
	CenterName    string
	CenterAddress string

	TableID     string
	TableNumber string

	ActaFilename  string
	ActaBucketURL string
	ActaStaticURL string

	ResultsURL string // to be filled later
}

type ApiResponse struct {
	Error  string `json:"error"`
	Person struct {
		RE_CO_FULLID          string // "V123123",
		RE_DS_FIRST_NAME      string // "PEPE",
		RE_DS_SECOND_NAME     string // "JOSE",
		RE_DS_FIRST_LASTNAME  string // "TRUENO",
		RE_DS_SECOND_LASTNAME string // "RAYO",
		RE_CD_GENDER          string // "F",
		RE_DT_BIRTHDATE       string // "1988-12-16T00:00:00.000Z",
		RE_CD_STATE           string // "13",
		RE_DS_CNE_ID          string // "130901073",
		RE_NU_TOMO            string // null,
		IT_CD_ROW             int    // 11,
		IT_CD_PAGE            int    // 97,
		TB_DS_TABLE           int    // 2,
		TB_NU_COUNT           int    // 704,
		TB_DS_TERM_MIN        string // "35",
		TB_DS_TERM_MAX        string // "67",
		TB_DS_CODE_QR         string // null,
		RE_DS_TERM_ID         int    // 61,
		ST_DS_STATE           string // "EDO. MIRANDA",
		MU_DS_MUN             string // "MP. SUCRE",
		PA_DS_PAR             string // "PQ. PETARE",
		PC_CO_CNE             string // "130901073",
		PC_DS_CENTER          string // "UNIDAD EDUCATIVA MUNICIPAL GUAICAIPURO",
		PC_DS_ADDRESS         string // "BARRIO GUAICAIPURO PETARE DERECHA CALLE PRINCIPAL. IZQUIERDA CALLE PRINCIPAL. FRENTE CALLE PRINCIPAL DE GUAICAIPURO REAL DE MACA PETARE CASA",
		AU_CO_CREATE_USER     string // "1",
		AU_CO_DROP_USER       string // null,
		AU_CO_MODIFY_USER     string // "1",
		AU_DT_CREATE_DATE     string // "2024-03-10T05:16:53.080Z",
		AU_DT_DROP_DATE       string // null,
		AU_DT_MODIFY_DATE     string // "2024-06-07T04:10:50.743Z"
	}
	Acta struct {
		DO_CD_DOCUMENT       string //  "58544",
		DO_DS_NAME           string //  "656297_785221_0738Acta0589.jpg",
		DO_DS_BUCKET         string //  "elecciones2024ve",
		DO_CD_SESSION        string //  "127df6ad-e42c-41e1-a0c3-568eb00af313",
		DO_CD_TYPE           string //  null,
		DO_DS_SERIAL         string //  "656297",
		DO_BO_BOUND          string //  null,
		DO_BO_DUPLICATE      string //  null,
		DO_BO_AUTO_DETECT    string //  null,
		DO_NU_QUALITY        string //  null,
		DO_BO_PUBLISH        string //  null,
		DO_CD_CHANNEL        int    //  0,
		DO_CD_STATE          string //  "13",
		DO_CD_MUN            string //  "174",
		DO_CD_PAR            string //  "604",
		DO_CD_CENTER         string //  "4430",
		DO_CO_CNE_CENTER     string //  "130901073",
		DO_CD_TABLE          string //  "18047",
		DO_NU_TABLE          string //  "2",
		DO_CD_PUBLISH        string //  null,
		DO_CO_STAGE          string //  "TT",
		DO_DT_A1             string //  "2024-07-29T20:05:32.177Z",
		DO_DT_P1             string //  null,
		DO_DT_P2             string //  null,
		DO_DT_RC             string //  null,
		AU_DT_TAKE           string //  null,
		AU_CO_TAKE           string //  null,
		DO_BO_TOTALIZED      bool   //  true,
		DO_CD_SESSION_AUTO   string //  "af63c6cd-2807-45d8-93c7-7fc96c0dce70",
		DO_BO_MASKED         string //  null,
		DO_DS_RAWDATA        string //  null,
		DO_BO_MASKED_SESSION string //  null,
		AU_CO_CREATE_USER    string //  "2",
		AU_CO_MODIFY_USER    string //  "1",
		AU_CO_DROP_USER      string //  null,
		AU_DT_CREATE_DATE    string //  "2024-07-29T20:02:05.697Z",
		AU_DT_MODIFY_DATE    string //  "2024-07-29T20:05:32.177Z",
		AU_DT_DROP_DATE      string //  null
	}
}

func Resolve(cedula string) (*CedulaInfo, error) {
	return retry(func() (*CedulaInfo, error) {
		return fetch(cedula)
	}, 3, 1000)
}

func fetch(cedula string) (*CedulaInfo, error) {
	r, err := http.Get(fmt.Sprintf("%s?cdi=V%s", apiEndpoint, cedula))
	if err != nil {
		return nil, err
	}

	body, err := io.ReadAll(r.Body)
	if err != nil {
		return nil, err
	}

	resp := ApiResponse{}
	err = json.Unmarshal(body, &resp)
	if err != nil {
		return nil, err
	}

	if resp.Error != "" {
		return nil, errors.Errorf("could not resolve cedula %s", cedula)
	}

	return &CedulaInfo{
		Cedula: resp.Person.RE_CO_FULLID,

		StateID:   resp.Person.RE_CD_STATE,
		StateName: resp.Person.ST_DS_STATE,

		CountyID:   resp.Acta.DO_CD_MUN,
		CountyName: resp.Person.MU_DS_MUN,

		ParishID:   resp.Acta.DO_CD_PAR,
		ParishName: resp.Person.PA_DS_PAR,

		CenterOldID:   resp.Acta.DO_CD_CENTER,
		CenterID:      resp.Person.RE_DS_CNE_ID,
		CenterName:    resp.Person.PC_DS_CENTER,
		CenterAddress: resp.Person.PC_DS_ADDRESS,

		TableID:     resp.Acta.DO_CD_TABLE,
		TableNumber: resp.Acta.DO_NU_TABLE,

		ActaFilename:  resp.Acta.DO_DS_NAME,
		ActaBucketURL: lo.Ternary(resp.Acta.DO_DS_NAME == "", "", fmt.Sprintf("https://elecciones2024ve.s3.amazonaws.com/%s", resp.Acta.DO_DS_NAME)),
		ActaStaticURL: lo.Ternary(resp.Acta.DO_DS_NAME == "", "", fmt.Sprintf("https://static.resultadosconvzla.com/%s", resp.Acta.DO_DS_NAME)),
	}, nil
}
