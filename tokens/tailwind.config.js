/** @type {import('tailwindcss').Config} */
export default {
  "theme": {
    "extend": {
      "colors": {
        "primary": "#0e0f12",
        "secondary": "#f1f0ec",
        "accent": "#ff2a36",
        "neutral": {
          "50": "#fbfaf6",
          "100": "#f1f0ec",
          "150": "#e7e6e2",
          "200": "#dad9d6",
          "300": "#bebebb",
          "400": "#989897",
          "500": "#787979",
          "600": "#5c5c5d",
          "700": "#434445",
          "800": "#2d2e30",
          "850": "#222325",
          "900": "#18191c",
          "950": "#0e0f12"
        },
        "success": "#3aba6a",
        "warning": "#f2b036",
        "error": "#d4101e",
        "info": "#468de5"
      },
      "fontFamily": {
        "heading": [
          "Archivo",
          "sans-serif"
        ],
        "body": [
          "Instrument Sans",
          "sans-serif"
        ],
        "mono": [
          "Martian Mono",
          "monospace"
        ]
      },
      "fontSize": {
        "label": [
          "12px",
          {
            "lineHeight": "1.3"
          }
        ],
        "small": [
          "14px",
          {
            "lineHeight": "1.45"
          }
        ],
        "body": [
          "16px",
          {
            "lineHeight": "1.55"
          }
        ],
        "lead": [
          "21px",
          {
            "lineHeight": "1.45"
          }
        ],
        "h4": [
          "21px",
          {
            "lineHeight": "1.15"
          }
        ],
        "h3": [
          "28px",
          {
            "lineHeight": "1.1"
          }
        ],
        "h2": [
          "38px",
          {
            "lineHeight": "1.05"
          }
        ],
        "h1": [
          "50px",
          {
            "lineHeight": "1.02"
          }
        ],
        "display": [
          "67px",
          {
            "lineHeight": "1.0"
          }
        ],
        "hero": [
          "90px",
          {
            "lineHeight": "0.96"
          }
        ]
      },
      "spacing": {
        "0": "0px",
        "1": "4px",
        "2": "8px",
        "3": "12px",
        "4": "16px",
        "5": "24px",
        "6": "32px",
        "7": "48px",
        "8": "64px",
        "9": "96px",
        "10": "128px"
      },
      "boxShadow": {
        "none": "none"
      },
      "borderRadius": {
        "none": "0px",
        "sm": "4px",
        "md": "8px",
        "lg": "14px",
        "tile": "22%",
        "full": "9999px"
      },
      "borderWidth": {
        "thin": "1px",
        "medium": "2px",
        "thick": "4px"
      },
      "transitionDuration": {
        "fast": "120ms",
        "normal": "200ms",
        "slow": "320ms"
      },
      "transitionTimingFunction": {
        "ease-out": "cubic-bezier(0.2, 0, 0, 1)",
        "ease-in-out": "cubic-bezier(0.6, 0, 0.2, 1)"
      },
      "backgroundImage": {}
    }
  }
};
